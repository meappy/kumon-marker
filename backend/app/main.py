"""FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers import worksheets, auth, settings as settings_router, jobs

app = FastAPI(
    title=settings.app_name,
    description="Automated Kumon worksheet marking system",
    version=settings.app_version,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(worksheets.router, prefix="/api", tags=["worksheets"])
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(settings_router.router, prefix="/api", tags=["settings"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])

# Serve static frontend (when built)
static_dir = Path(__file__).parent.parent / "frontend" / "dist"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")


@app.get("/api")
async def root():
    """API root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }
