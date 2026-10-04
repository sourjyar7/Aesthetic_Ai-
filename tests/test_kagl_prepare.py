import io
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
from PIL import Image

from catalog.kagl.prepare import MAX_SIDE, prepare, write_outputs


def _image_bytes(size: tuple[int, int], mode: str = "RGB", fmt: str = "JPEG") -> bytes:
    buffer = io.BytesIO()
    Image.new(mode, size, color=(200, 30, 30, 255)[: len(mode)]).save(buffer, fmt)
    return buffer.getvalue()


def _record(item_id: int, category1: str, category3: str, image: bytes) -> dict[str, Any]:
    return {
        "image": {"bytes": image, "path": f"{item_id}.jpg"},
        "gender": "Men",
        "category1": category1,
        "category2": "Topwear",
        "category3": category3,
        "baseColour": "Red",
        "season": "Summer",
        "year": 2012.0,
        "usage": "Casual",
        "text": f"Test product {item_id}",
        "item_ID": item_id,
    }


def _write_fake_shard(path: Path) -> None:
    """A miniature KAGL shard with the same column layout as the real one."""
    records = [
        _record(3, "Apparel", "Shirts", _image_bytes((1800, 2400))),  # big JPEG -> resized
        _record(1, "Personal Care", "Perfume", _image_bytes((100, 100))),  # dropped category
        _record(2, "Apparel", "Tshirts", b"not an image"),  # corrupt bytes -> skipped
        _record(4, "Footwear", "Heels", _image_bytes((300, 200), "RGBA", "PNG")),  # PNG + alpha
    ]
    pq.write_table(pa.Table.from_pylist(records), path)


def test_prepare_filters_resizes_and_skips(tmp_path: Path) -> None:
    shard = tmp_path / "shard.parquet"
    _write_fake_shard(shard)
    out_dir = tmp_path / "out"

    rows = prepare([str(shard)], out_dir)

    # Perfume (wrong category) and the corrupt image are dropped; the others are kept.
    assert sorted(row["item_ID"] for row in rows) == [3, 4]
    assert all(row["image_path"] == f"images/{row['item_ID']}.jpg" for row in rows)

    with Image.open(out_dir / "images" / "3.jpg") as big:
        assert big.format == "JPEG" and big.mode == "RGB"
        assert big.size == (MAX_SIDE * 3 // 4, MAX_SIDE)  # 1800x2400 -> 384x512, ratio kept
    with Image.open(out_dir / "images" / "4.jpg") as small:
        assert small.mode == "RGB"  # transparency removed so it can be a JPEG
        assert small.size == (300, 200)  # never enlarged
    assert not list((out_dir / "images").glob("*.tmp"))


def test_prepare_is_resumable(tmp_path: Path) -> None:
    shard = tmp_path / "shard.parquet"
    _write_fake_shard(shard)
    out_dir = tmp_path / "out"
    prepare([str(shard)], out_dir)
    first_mtime = (out_dir / "images" / "3.jpg").stat().st_mtime_ns

    rows = prepare([str(shard)], out_dir)

    assert len(rows) == 2
    assert (out_dir / "images" / "3.jpg").stat().st_mtime_ns == first_mtime  # not rewritten


def test_write_outputs_sorts_and_counts(tmp_path: Path) -> None:
    shard = tmp_path / "shard.parquet"
    _write_fake_shard(shard)
    out_dir = tmp_path / "out"

    write_outputs(prepare([str(shard)], out_dir), out_dir)

    table = pq.read_table(out_dir / "products.parquet")
    assert table["item_ID"].to_pylist() == [3, 4]
    assert "image_path" in table.schema.names
    stats = (out_dir / "stats.json").read_text()
    assert '"products": 2' in stats and '"Heels": 1' in stats
