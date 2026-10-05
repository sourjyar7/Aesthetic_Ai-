"""Load each embedding model and time it on real product photos.

Usage: uv run python -m ai.embeddings.smoke [--models KEY ...] [--images N]
"""

import argparse
import time
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq
from PIL import Image

from ai.embeddings import MODELS, load_embedder
from ai.embeddings.open_clip_embedder import default_device

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_DIR = REPO_ROOT / "data" / "processed" / "kagl"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", default=sorted(MODELS), choices=sorted(MODELS))
    parser.add_argument("--images", type=int, default=64, help="how many product photos to embed")
    args = parser.parse_args()

    table = pq.read_table(CATALOG_DIR / "products.parquet", columns=["image_path"])
    paths = [path for path in table["image_path"].to_pylist() if path is not None][: args.images]
    # .convert("RGB") forces the file to be read now, so disk time isn't counted as model time.
    images = [Image.open(CATALOG_DIR / path).convert("RGB") for path in paths]
    print(f"device: {default_device()} · {len(images)} product photos\n")

    for key in args.models:
        started = time.perf_counter()
        embedder = load_embedder(key)
        load_seconds = time.perf_counter() - started

        embedder.encode_images(images[:8])  # warm-up: the first GPU call is always slow

        started = time.perf_counter()
        vectors = embedder.encode_images(images)
        image_seconds = time.perf_counter() - started

        started = time.perf_counter()
        embedder.encode_texts(["distressed light-wash jeans"])
        text_ms = (time.perf_counter() - started) * 1000

        norms = np.linalg.norm(vectors, axis=1)
        print(
            f"{key:22s} dim={embedder.dim:<4d} load={load_seconds:5.1f}s  "
            f"images={len(images) / image_seconds:6.1f}/s  text={text_ms:5.1f}ms  "
            f"norms={norms.min():.4f}..{norms.max():.4f}"
        )


if __name__ == "__main__":
    main()
