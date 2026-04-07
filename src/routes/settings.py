"""Settings routes — connection status, OAuth management."""

import os
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/api/settings/connections")
async def check_connections():
    """Check status of all API connections."""
    connections = []

    # YouTube
    token_path = Path(__file__).resolve().parent.parent.parent / "token.json"
    yt_connected = token_path.exists()
    connections.append({
        "name": "YouTube API",
        "connected": yt_connected,
        "status": "Connected — token.json found" if yt_connected else "Not connected — run OAuth setup",
        "action": "window.location='/api/settings/youtube/connect'" if not yt_connected else "",
        "action_label": "Connect" if not yt_connected else "",
    })

    # Meta / Facebook
    meta_token = os.environ.get("META_ACCESS_TOKEN", "")
    fb_page = os.environ.get("FACEBOOK_PAGE_ID", "")
    meta_connected = bool(meta_token and fb_page)
    connections.append({
        "name": "Meta (Facebook/Instagram)",
        "connected": meta_connected,
        "status": f"Connected — Page ID: {fb_page[:8]}..." if meta_connected else "Not configured — set META_ACCESS_TOKEN and FACEBOOK_PAGE_ID in .env",
        "action": "",
        "action_label": "",
    })

    # Twitter
    tw_key = os.environ.get("TWITTER_API_KEY", "")
    tw_token = os.environ.get("TWITTER_ACCESS_TOKEN", "")
    tw_connected = bool(tw_key and tw_token)
    connections.append({
        "name": "Twitter / X",
        "connected": tw_connected,
        "status": "Connected — API keys configured" if tw_connected else "Not configured — set TWITTER_API_KEY and related env vars in .env",
        "action": "",
        "action_label": "",
    })

    # Anthropic (Claude)
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    connections.append({
        "name": "Anthropic (Claude AI)",
        "connected": bool(anthropic_key),
        "status": "Connected — API key set" if anthropic_key else "Not configured — set ANTHROPIC_API_KEY in .env for audit tool",
        "action": "",
        "action_label": "",
    })

    # OpenAI (DALL-E)
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    connections.append({
        "name": "OpenAI (DALL-E)",
        "connected": bool(openai_key),
        "status": "Connected — API key set" if openai_key else "Not configured — set OPENAI_API_KEY in .env for scripture cards",
        "action": "",
        "action_label": "",
    })

    return {"connections": connections}


@router.post("/api/settings/youtube/connect")
async def youtube_connect():
    """Trigger YouTube OAuth flow."""
    try:
        from src.youtube.auth import get_credentials
        import asyncio
        await asyncio.to_thread(get_credentials)
        return {"message": "YouTube connected successfully"}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)
