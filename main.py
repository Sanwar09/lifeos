"""
LifeOS AI — FastAPI Application Entry Point
Your Personal AI Chief of Staff
Powered by Lemma SDK
"""
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from contextlib import asynccontextmanager
import os
import logging

from config import settings
from database import init_db
from api.routes import router
from api.auth import router as auth_router, get_current_user_optional

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

    # Ensure upload and workspace directories exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(os.path.abspath("./workspace"), exist_ok=True)

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
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

# Determine static files directory robustly
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    # Fallback to current working directory static
    static_dir = os.path.abspath("static")

# ─── Static file serving (for uploaded documents and static frontend assets) ──
if os.path.exists(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", tags=["root"])
async def root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "name": "LifeOS AI",
        "tagline": "Your Personal AI Chief of Staff",
        "version": "1.0.0",
        "status": "running",
        "powered_by": "Lemma SDK",
        "docs": "/api/docs",
    }


@app.get("/category.html", tags=["root"])
async def category_page():
    """Serve category.html cleanly from the static directory."""
    cat_path = os.path.join(static_dir, "category.html")
    if os.path.exists(cat_path):
        return FileResponse(cat_path)
    for fallback in ["category.html", "frontend/public/category.html"]:
        if os.path.exists(fallback):
            return FileResponse(fallback)
    raise HTTPException(status_code=404, detail="category.html not found")


@app.get("/dashboard.html", tags=["root"])
async def dashboard_page(request: Request):
    """
    Serve dashboard.html cleanly with authentication check.
    Redirects to Google login if unauthenticated in production, or allows local dev access.
    """
    # Check session cookie or bearer token
    token = request.cookies.get("access_token")
    auth_header = request.headers.get("Authorization")
    
    if not token and not auth_header and settings.environment == "production" and settings.google_client_id:
        # Redirect unauthenticated users in production to login page
        return RedirectResponse(url="/api/auth/google/login", status_code=303)

    dash_path = os.path.join(static_dir, "dashboard.html")
    if os.path.exists(dash_path):
        return FileResponse(dash_path)
    
    for fallback in ["dashboard.html", "frontend/public/dashboard.html"]:
        if os.path.exists(fallback):
            return FileResponse(fallback)
    raise HTTPException(status_code=404, detail="dashboard.html not found")


@app.get("/dashboard", tags=["root"])
async def dashboard_alias(request: Request):
    return await dashboard_page(request)


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