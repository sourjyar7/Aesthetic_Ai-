"""Embedding models behind one interface: `load_embedder(key)` returns an `Embedder`."""

from ai.embeddings.base import Embedder, Vectors
from ai.embeddings.open_clip_embedder import OpenClipEmbedder
from ai.embeddings.registry import MODELS, ModelSpec

__all__ = ["MODELS", "Embedder", "ModelSpec", "OpenClipEmbedder", "Vectors", "load_embedder"]


def load_embedder(model_key: str, device: str | None = None) -> Embedder:
    if model_key not in MODELS:
        raise ValueError(f"unknown model {model_key!r}; choose from {sorted(MODELS)}")
    return OpenClipEmbedder(MODELS[model_key], device=device)
