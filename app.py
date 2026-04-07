"""
YouTube Optimizer Dashboard — AI Bible Gospels
Unified web dashboard for channel management, analytics, social media, and content tools.

Usage:
    pip install -r requirements.txt
    python app.py
"""

import os
import sys
from pathlib import Path

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

app = FastAPI(title="YouTube Optimizer — AI Bible Gospels")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

# Lazy YouTube client singleton
_yt_client = None


def get_yt_client():
    """Lazily create YouTubeClient on first API call to avoid OAuth popup on startup."""
    global _yt_client
    if _yt_client is None:
        from src.youtube.client import YouTubeClient
        _yt_client = YouTubeClient()
    return _yt_client


# Register all route modules
from src.routes import dashboard, videos, playlists, analytics, audit, social, tools, settings

app.include_router(dashboard.router)
app.include_router(videos.router, prefix="/api")
app.include_router(playlists.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(audit.router)
app.include_router(social.router)
app.include_router(tools.router)
app.include_router(settings.router)


# Page routes — serve Jinja2 templates
@app.get("/videos", response_class=HTMLResponse)
async def videos_page(request: Request):
    return templates.TemplateResponse("videos.html", {"request": request, "page": "videos"})


@app.get("/playlists", response_class=HTMLResponse)
async def playlists_page(request: Request):
    return templates.TemplateResponse("playlists.html", {"request": request, "page": "playlists"})


@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request, "page": "analytics"})


@app.get("/audit", response_class=HTMLResponse)
async def audit_page(request: Request):
    return templates.TemplateResponse("audit.html", {"request": request, "page": "audit"})


@app.get("/social", response_class=HTMLResponse)
async def social_page(request: Request):
    return templates.TemplateResponse("social.html", {"request": request, "page": "social"})


@app.get("/tools", response_class=HTMLResponse)
async def tools_page(request: Request):
    return templates.TemplateResponse("tools.html", {"request": request, "page": "tools"})


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request, "page": "settings"})


@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "page": "about"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
