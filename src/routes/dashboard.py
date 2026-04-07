"""Dashboard routes — channel status, recent uploads, analytics summary, quota."""

import asyncio
from datetime import date, timedelta
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    from app import templates
    return templates.TemplateResponse("dashboard.html", {"request": request, "page": "dashboard"})


@router.get("/api/channel-status")
async def channel_status():
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        info = await asyncio.to_thread(client.get_channel_info)
        if not info:
            return JSONResponse({"error": "No channel info"}, status_code=404)
        stats = info["statistics"]
        return {
            "subscribers": int(stats.get("subscriberCount", 0)),
            "views": int(stats.get("viewCount", 0)),
            "videos": int(stats.get("videoCount", 0)),
            "name": info["snippet"]["title"],
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/api/recent-uploads")
async def recent_uploads():
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        videos = await asyncio.to_thread(client.list_videos, 10)
        return {
            "videos": [
                {
                    "id": v["id"],
                    "title": v["snippet"]["title"],
                    "published": v["snippet"]["publishedAt"][:10],
                    "views": int(v["statistics"].get("viewCount", 0)),
                    "likes": int(v["statistics"].get("likeCount", 0)),
                }
                for v in videos
            ]
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/api/analytics-summary")
async def analytics_summary():
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        end = date.today()
        start = end - timedelta(days=28)

        def _query():
            return client.analytics.reports().query(
                ids=f"channel=={client.channel_id}",
                startDate=str(start),
                endDate=str(end),
                metrics="views,estimatedMinutesWatched,averageViewDuration,subscribersGained,likes,comments",
            ).execute()

        result = await asyncio.to_thread(_query)
        if result.get("rows"):
            row = result["rows"][0]
            return {
                "views": row[0],
                "watch_time_minutes": row[1],
                "avg_view_duration": row[2],
                "subscribers_gained": row[3],
                "likes": row[4],
                "comments": row[5],
            }
        return {"views": 0, "watch_time_minutes": 0, "avg_view_duration": 0, "subscribers_gained": 0}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/api/quota")
async def quota_status():
    """Return estimated quota usage for the current session."""
    return {
        "used": 0,
        "limit": 10000,
        "note": "Quota tracking is session-based. Resets daily at midnight PT.",
    }
