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
from pathlib import Path

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

# ─── Security Header & CSP Middleware ───────────────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https:; "
        "object-src 'none';"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# ─── Routes ──────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

# Determine static files directory robustly
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    static_dir = os.path.abspath("static")

# Ensure static dir exists
os.makedirs(static_dir, exist_ok=True)

# ─── Static file serving ────────────────────────────────────────────────────
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
        "dashboard": "/dashboard.html"
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
@app.get("/dashboard", tags=["root"])
async def dashboard_page(request: Request, user = Depends(get_current_user_optional)):
    """
    Serve dashboard.html securely.
    """
    if settings.environment == "production" and not user and not request.cookies.get("access_token"):
        return RedirectResponse(url="/api/auth/login", status_code=303)

    dash_path = os.path.join(static_dir, "dashboard.html")
    if os.path.exists(dash_path):
        return FileResponse(dash_path)
        
    for fallback in ["dashboard.html", "frontend/public/dashboard.html"]:
        if os.path.exists(fallback):
            return FileResponse(fallback)
            
    raise HTTPException(status_code=404, detail="dashboard.html not found")