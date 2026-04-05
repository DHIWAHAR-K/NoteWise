from pydantic import BaseModel, Field


class SOAPNote(BaseModel):
    subjective: str = Field(..., description="Patient's reported symptoms, history, and chief complaint")
    objective: str = Field(..., description="Vitals, exam findings, and lab/imaging results from transcript")
    assessment: str = Field(..., description="Clinical impression and diagnoses")
    plan: str = Field(..., description="Treatment plan, medications, referrals, and follow-up")
    citations: list[str] = Field(default_factory=list, description="Source IDs from RAG context used")
    disclaimer: str = Field(default="NOT for clinical use.", description="Mandatory disclaimer")


class SOAPRequest(BaseModel):
    transcript: str = Field(..., min_length=1, description="Doctor-patient conversation transcript")
    rag_context: str | None = Field(None, description="Optional RAG context from /rag/query")


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to synthesize")
