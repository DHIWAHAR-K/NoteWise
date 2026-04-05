import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import transcribe, rag, imaging, soap

load_dotenv()

app = FastAPI(title="NoteWise API", description="AI Medical Voice Scribe — NOT for clinical use.")

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcribe.router)
app.include_router(rag.router)
app.include_router(imaging.router)
app.include_router(soap.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
