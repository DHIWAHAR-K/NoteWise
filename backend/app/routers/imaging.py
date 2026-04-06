from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.imaging.moonshot_classify import classify_image_moonshot
from app.settings import get_moonshot_api_key

router = APIRouter(prefix="/imaging", tags=["imaging"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"}


class ImagingResponse(BaseModel):
    label: str
    confidence: float
    model_id: str
    disclaimer: str


@router.post("/classify", response_model=ImagingResponse)
async def classify_image(file: UploadFile = File(...)):
    """Classify or describe an uploaded image via Moonshot vision API.

    Returns label, confidence, model_id, and a clinical disclaimer.
    NOT for clinical use.
    """
    if not get_moonshot_api_key():
        raise HTTPException(
            status_code=503,
            detail="Image understanding is not configured (missing MOONSHOT_API_KEY).",
        )

    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported file type '{file.content_type}'. Accepted: JPEG, PNG, WEBP, BMP, TIFF.",
        )

    data = await file.read()
    if len(data) == 0:
        raise HTTPException(status_code=422, detail="Empty file uploaded.")

    try:
        result = await classify_image_moonshot(data, file.content_type)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Classification error: {exc}") from exc

    return ImagingResponse(**result)
