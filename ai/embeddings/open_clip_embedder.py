"""One adapter for every open_clip model (CLIP and SigLIP families)."""

from collections.abc import Sequence

import numpy as np
import open_clip
import torch
from PIL import Image

from ai.embeddings.base import Vectors
from ai.embeddings.registry import ModelSpec


def default_device() -> str:
    """Apple GPU (MPS) when available, otherwise CPU."""
    return "mps" if torch.backends.mps.is_available() else "cpu"


class OpenClipEmbedder:
    def __init__(self, spec: ModelSpec, device: str | None = None, batch_size: int = 64) -> None:
        self.model_key = spec.key
        self.device = device or default_device()
        self.batch_size = batch_size
        model, _, self._preprocess = open_clip.create_model_and_transforms(
            spec.open_clip_name, pretrained=spec.pretrained
        )
        self._tokenizer = open_clip.get_tokenizer(spec.open_clip_name)
        self._model = model.to(self.device).eval()
        # Ask the model itself how long its vectors are (768 for SigLIP, 512 for ViT-B/32).
        self.dim = int(self.encode_texts(["dimension probe"]).shape[1])

    def encode_images(self, images: Sequence[Image.Image]) -> Vectors:
        chunks: list[Vectors] = []
        for start in range(0, len(images), self.batch_size):
            batch = images[start : start + self.batch_size]
            pixels = torch.stack([self._preprocess(image.convert("RGB")) for image in batch])
            with torch.inference_mode():
                vectors = self._model.encode_image(pixels.to(self.device), normalize=True)
            chunks.append(vectors.float().cpu().numpy())
        return np.concatenate(chunks)

    def encode_texts(self, texts: Sequence[str]) -> Vectors:
        chunks: list[Vectors] = []
        for start in range(0, len(texts), self.batch_size):
            batch = [text.lower() for text in texts[start : start + self.batch_size]]
            tokens = self._tokenizer(batch)
            with torch.inference_mode():
                vectors = self._model.encode_text(tokens.to(self.device), normalize=True)
            chunks.append(vectors.float().cpu().numpy())
        return np.concatenate(chunks)
