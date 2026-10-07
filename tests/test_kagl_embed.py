from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from ai.embeddings import Vectors
from catalog.kagl.embed import embed_catalog


class FakeEmbedder:
    """Follows the Embedder contract; vectors encode the image's redness and the text's length."""

    model_key = "fake"
    dim = 4

    def __init__(self) -> None:
        self.image_calls = 0

    def encode_images(self, images: Sequence[Image.Image]) -> Vectors:
        self.image_calls += 1
        rows = [[float(np.asarray(image)[0, 0, 0]), 1.0, 0.0, 0.0] for image in images]
        return _unit(np.array(rows))

    def encode_texts(self, texts: Sequence[str]) -> Vectors:
        rows = [[float(len(text)), 0.0, 1.0, 0.0] for text in texts]
        return _unit(np.array(rows))


def _unit(matrix: np.ndarray[Any, Any]) -> Vectors:
    return (matrix / np.linalg.norm(matrix, axis=1, keepdims=True)).astype(np.float32)


def test_embed_catalog_writes_aligned_vectors(tmp_path: Path) -> None:
    catalog_dir = tmp_path / "catalog"
    (catalog_dir / "images").mkdir(parents=True)
    products: list[dict[str, Any]] = []
    for item_id, red in [(10, 40), (20, 140), (30, 240)]:
        Image.new("RGB", (8, 8), (red, 0, 0)).save(catalog_dir / "images" / f"{item_id}.jpg")
        products.append(
            {"item_ID": item_id, "text": f"product {item_id}", "image_path": f"images/{item_id}.jpg"}
        )
    products[1]["text"] = None  # a missing title must not crash the text encoder
    out_dir = tmp_path / "out"
    fake = FakeEmbedder()

    meta = embed_catalog(fake, products, catalog_dir, out_dir, chunk_size=2)

    assert fake.image_calls == 2  # 3 products in chunks of 2 -> two calls
    image_vectors = np.load(out_dir / "image_vectors.npy")
    text_vectors = np.load(out_dir / "text_vectors.npy")
    assert image_vectors.shape == (3, 4) and text_vectors.shape == (3, 4)
    assert np.load(out_dir / "item_ids.npy").tolist() == [10, 20, 30]
    # Rows stay in product order: the redder the photo, the bigger the first number.
    assert image_vectors[0, 0] < image_vectors[1, 0] < image_vectors[2, 0]
    assert meta["count"] == 3 and meta["model_key"] == "fake" and meta["dim"] == 4