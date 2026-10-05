"""The contract every embedding model adapter satisfies."""

from collections.abc import Sequence
from typing import Protocol

import numpy as np
import numpy.typing as npt
from PIL import Image

# An (N, dim) matrix of float32 vectors, each scaled to length 1.
Vectors = npt.NDArray[np.float32]


class Embedder(Protocol):
    model_key: str
    dim: int

    def encode_images(self, images: Sequence[Image.Image]) -> Vectors: ...

    def encode_texts(self, texts: Sequence[str]) -> Vectors: ...
