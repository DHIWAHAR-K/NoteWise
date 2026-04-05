"""Image classifier — ViT via timm (CPU fallback for demo).

Lazy-loads weights on first call. Model: vit_base_patch16_224 pretrained on ImageNet.
For chest X-ray demo purposes only; NOT for clinical use.
"""
from __future__ import annotations

import io
from functools import lru_cache
from typing import Any

import torch
import timm
from PIL import Image
from timm.data import resolve_data_config, create_transform

MODEL_ID = "vit_base_patch16_224"
DISCLAIMER = "NOT for clinical use. Results are for demonstration only. Always consult a qualified radiologist."


@lru_cache(maxsize=1)
def _load_model() -> tuple[Any, Any]:
    model = timm.create_model(MODEL_ID, pretrained=True)
    model.eval()
    config = resolve_data_config({}, model=model)
    transform = create_transform(**config)
    return model, transform


def classify(image_bytes: bytes) -> dict[str, Any]:
    """Classify image bytes. Returns label, confidence, model_id, disclaimer."""
    model, transform = _load_model()

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Cannot decode image: {exc}") from exc

    tensor = transform(img).unsqueeze(0)  # type: ignore[arg-type]

    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=-1)
        top_prob, top_idx = probs.topk(1)

    label_idx = top_idx[0].item()
    confidence = float(top_prob[0].item())

    # Map ImageNet class index to human-readable label via timm's built-in labels
    try:
        from timm.data.imagenet_info import ImageNetInfo
        info = ImageNetInfo()
        label = info.index_to_description(int(label_idx))
    except Exception:
        label = f"class_{label_idx}"

    return {
        "label": label,
        "confidence": round(confidence, 4),
        "model_id": MODEL_ID,
        "disclaimer": DISCLAIMER,
    }
