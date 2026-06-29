"""
LifeOS AI — FastAPI Application Entry Point
Your Personal AI Chief of Staff
Powered by Lemma SDK
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import logging

from config import settings
from database import init_db
from api.routes import router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("lifeos")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic."""
    logger.info("🚀 LifeOS AI starting up...")
    await init_db()

    # Ensure upload directory exists
    os.makedirs(settings.upload_dir, exist_ok=True)

    # Initialize Lemma SDK connection
    if settings.lemma_enabled:
        from agents.base_agent import lemma
        logger.info("🔗 Connecting to Lemma SDK at %s", settings.lemma_server_url)

    logger.info("✅ LifeOS AI ready — Your Personal AI Chief of Staff")
    yield
    logger.info("👋 LifeOS AI shutting down")


app = FastAPI(
    title="LifeOS AI",
    description="Your Personal AI Chief of Staff — powered by Lemma SDK",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ─── CORS ───────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ──────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api")

# ─── Static file serving (for uploaded documents) ────────────────────────────
if os.path.exists(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/", tags=["root"])
async def root():
    return {
        "name": "LifeOS AI",
        "tagline": "Your Personal AI Chief of Staff",
        "version": "1.0.0",
        "status": "running",
        "powered_by": "Lemma SDK",
        "docs": "/api/docs",
    }


@app.get("/health", tags=["root"])
async def health():
    return {"status": "healthy", "service": "lifeos-ai"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )
