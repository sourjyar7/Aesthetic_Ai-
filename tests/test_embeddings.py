import numpy as np
import pytest
from PIL import Image

from ai.embeddings import MODELS, load_embedder


def test_unknown_model_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="unknown model"):
        load_embedder("not-a-model")


@pytest.mark.slow
@pytest.mark.parametrize("model_key", sorted(MODELS))
def test_embedder_shapes_norms_and_colour_sanity(model_key: str) -> None:
    embedder = load_embedder(model_key)
    red = Image.new("RGB", (224, 224), (220, 20, 20))
    blue = Image.new("RGB", (224, 224), (20, 40, 220))

    image_vecs = embedder.encode_images([red, blue])
    text_vecs = embedder.encode_texts(["a red image", "a blue image"])

    assert image_vecs.shape == (2, embedder.dim)
    assert text_vecs.shape == (2, embedder.dim)
    assert image_vecs.dtype == np.float32
    np.testing.assert_allclose(np.linalg.norm(image_vecs, axis=1), 1.0, atol=1e-3)

    similarity = image_vecs @ text_vecs.T  # rows: images, columns: texts
    assert similarity[0, 0] > similarity[0, 1]  # red image is closer to "a red image"
    assert similarity[1, 1] > similarity[1, 0]  # blue image is closer to "a blue image"
