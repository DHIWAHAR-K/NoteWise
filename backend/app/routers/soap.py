from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.soap.models import SOAPNote, SOAPRequest, TTSRequest
from app.soap.generator import generate_soap, text_to_speech

router = APIRouter(prefix="/soap", tags=["soap"])


@router.post("/generate", response_model=SOAPNote)
async def soap_generate(req: SOAPRequest):
    """Generate a structured SOAP note from a transcript and optional RAG context."""
    try:
        note = generate_soap(req.transcript, req.rag_context)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"SOAP generation error: {exc}") from exc
    return note


@router.post("/tts")
async def soap_tts(req: TTSRequest):
    """Convert text to speech via ElevenLabs. Returns audio/mpeg bytes."""
    try:
        audio = text_to_speech(req.text)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"TTS error: {exc}") from exc
    return Response(content=audio, media_type="audio/mpeg")
