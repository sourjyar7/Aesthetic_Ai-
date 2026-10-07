"""Embed every catalogue product (photo + title) with one or more models.

Usage: uv run python -m catalog.kagl.embed --all   (or: --models KEY [KEY ...])
Writes data/embeddings/kagl/<model_key>/: image_vectors.npy, text_vectors.npy,
item_ids.npy, meta.json
"""

import argparse
import json
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow.parquet as pq
from PIL import Image
from tqdm import tqdm

from ai.embeddings import MODELS, Embedder, load_embedder
from ai.embeddings.open_clip_embedder import default_device
from catalog.kagl.download import REPO_ID, REVISION
from catalog.kagl.prepare import OUT_DIR as CATALOG_DIR

REPO_ROOT = Path(__file__).resolve().parents[2]
EMBEDDINGS_DIR = REPO_ROOT / "data" / "embeddings" / "kagl"
CHUNK_SIZE = 256


def load_products(catalog_dir: Path) -> list[dict[str, Any]]:
    table = pq.read_table(
        catalog_dir / "products.parquet", columns=["item_ID", "text", "image_path"]
    )
    return table.to_pylist()


def embed_catalog(
    embedder: Embedder,
    products: list[dict[str, Any]],
    catalog_dir: Path,
    out_dir: Path,
    chunk_size: int = CHUNK_SIZE,
) -> dict[str, Any]:
    """Embed photos (in chunks) and titles, save them to out_dir, return the metadata."""
    out_dir.mkdir(parents=True, exist_ok=True)

    image_chunks = []
    started = time.perf_counter()
    for start in tqdm(range(0, len(products), chunk_size), desc=f"{embedder.model_key}"):
        chunk = products[start : start + chunk_size]
        images = [Image.open(catalog_dir / p["image_path"]).convert("RGB") for p in chunk]
        image_chunks.append(embedder.encode_images(images))
    image_seconds = time.perf_counter() - started

    image_vectors = np.concatenate(image_chunks)
    text_vectors = embedder.encode_texts([p["text"] or "" for p in products])
    item_ids = np.array([p["item_ID"] for p in products], dtype=np.int64)

    np.save(out_dir / "image_vectors.npy", image_vectors)
    np.save(out_dir / "text_vectors.npy", text_vectors)
    np.save(out_dir / "item_ids.npy", item_ids)

    return {
        "model_key": embedder.model_key,
        "dim": embedder.dim,
        "count": len(products),
        "seconds_images": round(image_seconds, 1),
        "images_per_second": round(len(products) / image_seconds, 1),
    }


def git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=REPO_ROOT
    )
    return result.stdout.strip() or "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--models", nargs="+", choices=sorted(MODELS))
    group.add_argument("--all", action="store_true", help="embed with every registered model")
    parser.add_argument("--force", action="store_true", help="re-embed even if outputs exist")
    parser.add_argument(
        "--device", choices=["mps", "cpu"], default=None, help="default: Apple GPU if available"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="photos per model call; lower = gentler on the GPU",
    )
    args = parser.parse_args()

    products = load_products(CATALOG_DIR)
    model_keys = sorted(MODELS) if args.all else args.models

    for key in model_keys:
        out_dir = EMBEDDINGS_DIR / key
        meta_path = out_dir / "meta.json"
        if meta_path.exists() and not args.force:
            existing = json.loads(meta_path.read_text())
            if existing.get("count") == len(products):
                print(f"{key}: already embedded ({existing['count']} products), skipping")
                continue

        device = args.device or default_device()
        embedder = load_embedder(key, device=device, batch_size=args.batch_size)
        meta = embed_catalog(embedder, products, CATALOG_DIR, out_dir)
        meta |= {
            "model": {
                "open_clip_name": MODELS[key].open_clip_name,
                "pretrained": MODELS[key].pretrained,
            },
            "dataset": {"repo_id": REPO_ID, "revision": REVISION},
            "device": device,
            "batch_size": args.batch_size,
            "git_commit": git_commit(),
            "created_at": datetime.now(UTC).isoformat(timespec="seconds"),
        }
        meta_path.write_text(json.dumps(meta, indent=2) + "\n")
        print(f"{key}: {meta['count']} products, {meta['images_per_second']} img/s -> {out_dir}")


if __name__ == "__main__":
    main()
