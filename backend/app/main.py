import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.routers import transcribe, rag, imaging, soap, chat

load_dotenv()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app import mongo as mongo_mod
    from app.settings import get_database_url, get_mongodb_uri
    from app.db.session import init_database, dispose_database

    url = get_database_url()
    if url:
        init_database(url)
    mongo_uri = get_mongodb_uri()
    if mongo_uri:
        await mongo_mod.connect(mongo_uri)
    yield
    await mongo_mod.disconnect()
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
app.include_router(chat.router)


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


@app.get("/health/mongo")
async def health_mongo():
    from app import mongo as mongo_mod
    from app.settings import get_mongodb_uri

    if not get_mongodb_uri() or not mongo_mod.is_configured():
        return {"mongo": "not_configured"}
    try:
        db = mongo_mod.get_db()
        await db.command("ping")
        return {"mongo": "ok"}
    except Exception:
        logger.error("mongo health check failed")
        return JSONResponse(status_code=503, content={"mongo": "error"})
