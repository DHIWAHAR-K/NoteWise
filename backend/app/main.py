import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.routers import transcribe, rag, imaging, soap

load_dotenv()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.settings import get_database_url
    from app.db.session import init_database, dispose_database

    url = get_database_url()
    if url:
        init_database(url)
    yield
    await dispose_database()


app = FastAPI(
    title="NoteWise API",
    description="AI Medical Voice Scribe — NOT for clinical use.",
    lifespan=lifespan,
)

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


@app.get("/health/db")
async def health_db():
    from app.settings import get_database_url
    from app.db.session import get_engine

    if not get_database_url():
        return {"database": "not_configured"}
    engine = get_engine()
    if engine is None:
        return {"database": "not_configured"}
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"database": "ok"}
    except Exception:
        logger.error("database health check failed")
        return JSONResponse(status_code=503, content={"database": "error"})
