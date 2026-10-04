"""Turn downloaded KAGL shards into resized JPEGs plus one product table (products.parquet)."""

import argparse
import io
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq
from huggingface_hub import hf_hub_download
from PIL import Image, UnidentifiedImageError
from tqdm import tqdm

from catalog.kagl.download import REPO_ID, REVISION, shard_filename

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "data" / "processed" / "kagl"
DEFAULT_SHARDS = [0, 11, 22, 33]
# Outfit pieces only; Personal Care, Free Items, Sporting Goods and Home are dropped.
KEEP_CATEGORIES = {"Apparel", "Footwear", "Accessories"}
METADATA_COLUMNS = [
    "item_ID",
    "gender",
    "category1",
    "category2",
    "category3",
    "baseColour",
    "season",
    "year",
    "usage",
    "text",
]
STATS_COLUMNS = ["category1", "category2", "category3", "gender", "baseColour", "usage"]
BATCH_SIZE = 256
MAX_SIDE = 512
JPEG_QUALITY = 90


def save_resized_jpeg(image_bytes: bytes, out_path: Path, max_side: int = MAX_SIDE) -> None:
    """Decode an image, shrink it so its longest side is at most max_side, save as JPEG."""
    with Image.open(io.BytesIO(image_bytes)) as image:
        # JPEG can't store transparency (RGBA) or palettes (P), so normalise to RGB.
        rgb = image.convert("RGB")
    rgb.thumbnail((max_side, max_side))  # in place; keeps the aspect ratio
    # Write to a temporary name first so an interrupted run never leaves a half-written image.
    tmp_path = out_path.with_suffix(".tmp")
    rgb.save(tmp_path, "JPEG", quality=JPEG_QUALITY)
    tmp_path.replace(out_path)


def prepare(shard_paths: list[str], out_dir: Path) -> list[dict[str, Any]]:
    """Process shards; return one metadata dict per kept product."""
    image_dir = out_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    skipped = Counter[str]()
    written = 0

    for shard_path in shard_paths:
        pf = pq.ParquetFile(shard_path)
        batches = pf.iter_batches(batch_size=BATCH_SIZE, columns=[*METADATA_COLUMNS, "image"])
        total = -(-pf.metadata.num_rows // BATCH_SIZE)  # ceiling division
        for batch in tqdm(batches, desc=Path(shard_path).name, total=total, unit="batch"):
            for record in batch.to_pylist():
                if record["category1"] not in KEEP_CATEGORIES:
                    skipped[f"category1={record['category1']}"] += 1
                    continue

                out_path = image_dir / f"{record['item_ID']}.jpg"
                if not out_path.exists():
                    try:
                        save_resized_jpeg(record["image"]["bytes"], out_path)
                        written += 1
                    except (UnidentifiedImageError, OSError, TypeError):
                        skipped["unreadable image"] += 1
                        continue

                row = {col: record[col] for col in METADATA_COLUMNS}
                row["image_path"] = str(out_path.relative_to(out_dir))
                rows.append(row)

    print(f"kept {len(rows)} products ({written} images written); skipped: {dict(skipped)}")
    return rows


def write_outputs(rows: list[dict[str, Any]], out_dir: Path) -> None:
    table = pa.Table.from_pylist(rows).sort_by("item_ID")
    pq.write_table(table, out_dir / "products.parquet")
    stats: dict[str, Any] = {"products": len(rows)}
    for col in STATS_COLUMNS:
        stats[col] = dict(Counter(row[col] for row in rows).most_common())
    (out_dir / "stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    print(f"wrote {out_dir / 'products.parquet'} and {out_dir / 'stats.json'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shards", type=int, nargs="+", default=DEFAULT_SHARDS)
    args = parser.parse_args()
    # local_files_only: never download here; run `python -m catalog.kagl.download` first.
    shard_paths = [
        hf_hub_download(
            REPO_ID,
            shard_filename(i),
            repo_type="dataset",
            revision=REVISION,
            local_files_only=True,
        )
        for i in sorted(set(args.shards))
    ]
    write_outputs(prepare(shard_paths, OUT_DIR), OUT_DIR)


if __name__ == "__main__":
    main()
