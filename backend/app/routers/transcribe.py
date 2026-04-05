import os
import tempfile
import assemblyai as aai
from fastapi import APIRouter, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

router = APIRouter(prefix="/transcribe", tags=["transcribe"])


def _get_client() -> aai.Transcriber:
    api_key = os.getenv("ASSEMBLYAI_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=503, detail="ASSEMBLYAI_API_KEY not configured")
    aai.settings.api_key = api_key
    return aai.Transcriber()


class TranscriptResponse(BaseModel):
    transcript: str
    confidence: float | None = None
    status: str = "completed"
    disclaimer: str = "NOT for clinical use."


@router.post("/upload", response_model=TranscriptResponse)
async def transcribe_upload(file: UploadFile = File(...)):
    """Upload an audio file and return its transcript via AssemblyAI."""
    allowed = {"audio/wav", "audio/mpeg", "audio/mp4", "audio/ogg", "audio/webm", "video/webm"}
    if file.content_type and file.content_type not in allowed:
        raise HTTPException(status_code=422, detail=f"Unsupported media type: {file.content_type}")

    transcriber = _get_client()

    with tempfile.NamedTemporaryFile(delete=False, suffix=_ext(file.filename)) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        result = transcriber.transcribe(tmp_path)
        if result.status == aai.TranscriptStatus.error:
            raise HTTPException(status_code=500, detail=f"Transcription error: {result.error}")
        return TranscriptResponse(
            transcript=result.text or "",
            confidence=result.confidence,
        )
    finally:
        os.unlink(tmp_path)


@router.websocket("/stream")
async def transcribe_stream(ws: WebSocket):
    """WebSocket endpoint — streams partial transcripts back to the client.

    Client sends raw audio bytes; server proxies to AssemblyAI real-time API.
    Partial transcripts are forwarded as JSON {"type":"partial","text":"..."}.
    """
    await ws.accept()
    api_key = os.getenv("ASSEMBLYAI_API_KEY", "")
    if not api_key:
        await ws.send_json({"type": "error", "detail": "ASSEMBLYAI_API_KEY not configured"})
        await ws.close()
        return

    aai.settings.api_key = api_key

    partial_texts: list[str] = []

    def on_data(transcript: aai.RealtimeTranscript):
        import asyncio
        if not transcript.text:
            return
        if isinstance(transcript, aai.RealtimeFinalTranscript):
            partial_texts.clear()
            asyncio.ensure_future(ws.send_json({"type": "final", "text": transcript.text}))
        else:
            asyncio.ensure_future(ws.send_json({"type": "partial", "text": transcript.text}))

    def on_error(error: aai.RealtimeError):
        import asyncio
        asyncio.ensure_future(ws.send_json({"type": "error", "detail": str(error)}))

    rt = aai.RealtimeTranscriber(
        sample_rate=16_000,
        on_data=on_data,
        on_error=on_error,
    )
    rt.connect()

    try:
        while True:
            chunk = await ws.receive_bytes()
            rt.stream(chunk)
    except WebSocketDisconnect:
        pass
    finally:
        rt.close()


def _ext(filename: str | None) -> str:
    if filename and "." in filename:
        return "." + filename.rsplit(".", 1)[-1]
    return ".wav"
