"""SOAP note generator — uses OpenAI structured output (JSON mode) + ElevenLabs TTS."""
import os
import json
from openai import OpenAI
from app.soap.models import SOAPNote

SYSTEM_PROMPT = """You are a clinical documentation assistant. Given a doctor-patient conversation transcript,
generate a structured SOAP note. Output ONLY valid JSON matching this schema:
{
  "subjective": "...",
  "objective": "...",
  "assessment": "...",
  "plan": "...",
  "citations": []
}
If optional RAG context is provided, incorporate it and list source_ids in citations.
Do NOT add any text outside the JSON. Do NOT include real patient identifying information.
Always be conservative — note when information is absent rather than inferring."""


def generate_soap(transcript: str, rag_context: str | None = None) -> SOAPNote:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not configured")

    client = OpenAI(api_key=api_key)

    user_content = f"TRANSCRIPT:\n{transcript}"
    if rag_context:
        user_content += f"\n\nRAG CONTEXT (medical reference, cite source_ids):\n{rag_context}"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
    )

    raw = response.choices[0].message.content or "{}"
    data = json.loads(raw)
    return SOAPNote(**data)


def text_to_speech(text: str) -> bytes:
    """Synthesize text to audio bytes via ElevenLabs."""
    api_key = os.environ.get("ELEVENLABS_API_KEY", "")
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # default: Rachel

    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY not configured")

    from elevenlabs import ElevenLabs

    el = ElevenLabs(api_key=api_key)
    audio_iter = el.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id="eleven_multilingual_v2",
    )
    return b"".join(audio_iter)
