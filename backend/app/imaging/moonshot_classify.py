"""Image description via Moonshot (Kimi) OpenAI-compatible vision API. NOT for clinical use."""

from __future__ import annotations

import base64
import json
import re
from typing import Any

from openai import APIError, AsyncOpenAI

from app.settings import (
    get_moonshot_api_key,
    get_moonshot_base_url,
    get_moonshot_vision_model,
)

DISCLAIMER = (
    "NOT for clinical use. Results are for demonstration only. "
    "Always consult a qualified radiologist."
)

_PROMPT = """You are helping with a non-clinical software demo that shows image understanding.
Reply with JSON only (no markdown fences), exactly one object:
{"label": "<one short line describing the main content>", "confidence": <number from 0 to 1 for your subjective certainty>}
If unsure about confidence, use 0.5."""


def _parse_model_text(text: str) -> tuple[str, float]:
    raw = text.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        data: Any = json.loads(raw)
        if isinstance(data, dict):
            label = str(data.get("label", "")).strip() or "unknown"
            conf = data.get("confidence", 0.5)
            try:
                c = float(conf)
            except (TypeError, ValueError):
                c = 0.5
            c = max(0.0, min(1.0, c))
            return label, c
    except json.JSONDecodeError:
        pass
    line = raw.split("\n", 1)[0].strip()
    return (line[:500] if line else "unknown"), 0.5


async def classify_image_moonshot(
    image_bytes: bytes,
    content_type: str | None,
) -> dict[str, Any]:
    api_key = get_moonshot_api_key()
    if not api_key:
        raise RuntimeError("MOONSHOT_API_KEY not configured")

    mime = (content_type or "image/jpeg").split(";")[0].strip().lower()
    if not mime.startswith("image/"):
        mime = "image/jpeg"

    b64 = base64.standard_b64encode(image_bytes).decode("ascii")
    data_url = f"data:{mime};base64,{b64}"
    model = get_moonshot_vision_model()

    client = AsyncOpenAI(api_key=api_key, base_url=get_moonshot_base_url())
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text", "text": _PROMPT},
                    ],
                }
            ],
            max_tokens=256,
        )
    except APIError as exc:
        raise RuntimeError(f"Moonshot API error: {exc}") from exc

    text = (resp.choices[0].message.content or "").strip()
    label, confidence = _parse_model_text(text)
    return {
        "label": label,
        "confidence": round(confidence, 4),
        "model_id": model,
        "disclaimer": DISCLAIMER,
    }
