"""The embedding models we evaluate. Model identifiers appear only in this file."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    key: str  # our short name, used everywhere else in the code
    open_clip_name: str  # what open_clip.create_model_and_transforms expects
    pretrained: str | None  # training-run tag, only needed for non-Hugging Face names
    licence: str
    notes: str


MODELS: dict[str, ModelSpec] = {
    spec.key: spec
    for spec in [
        ModelSpec(
            key="marqo-fashion-siglip",
            open_clip_name="hf-hub:Marqo/marqo-fashionSigLIP",
            pretrained=None,
            licence="Apache-2.0",
            notes="SigLIP ViT-B/16 fine-tuned on fashion products",
        ),
        ModelSpec(
            key="siglip2-base",
            open_clip_name="hf-hub:timm/ViT-B-16-SigLIP2",
            pretrained=None,
            licence="Apache-2.0",
            notes="General-purpose SigLIP 2, ViT-B/16 at 224 px",
        ),
        ModelSpec(
            key="openclip-b32",
            open_clip_name="ViT-B-32",
            pretrained="laion2b_s34b_b79k",
            licence="MIT",
            notes="Classic CLIP baseline trained on LAION-2B",
        ),
    ]
}
