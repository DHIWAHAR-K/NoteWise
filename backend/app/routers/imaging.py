from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.imaging.classifier import classify

router = APIRouter(prefix="/imaging", tags=["imaging"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"}


class ImagingResponse(BaseModel):
    label: str
    confidence: float
    model_id: str
    disclaimer: str


@router.post("/classify", response_model=ImagingResponse)
async def classify_image(file: UploadFile = File(...)):
    """Classify an uploaded image (chest X-ray or any image) via ViT.

    Returns label, confidence, model_id, and a clinical disclaimer.
    NOT for clinical use.
    """
    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type '{file.content_type}'. Accepted: JPEG, PNG, WEBP, BMP, TIFF.",
        )

    data = await file.read()
    if len(data) == 0:
        raise HTTPException(status_code=422, detail="Empty file uploaded.")

    try:
        result = classify(data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Classification error: {exc}") from exc

    return ImagingResponse(**result)
