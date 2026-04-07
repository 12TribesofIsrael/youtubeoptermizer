"""Video management routes — list, update, delete, thumbnails."""

import asyncio
import re
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None


class BulkAction(BaseModel):
    action: str  # "delete"
    video_ids: list[str]


def _parse_duration(iso_dur: str) -> str:
    """Convert ISO 8601 duration (PT5M22S) to human-readable."""
    dur = iso_dur.replace("PT", "")
    h = m = s = 0
    if "H" in dur:
        h, dur = dur.split("H")
        h = int(h)
    if "M" in dur:
        m, dur = dur.split("M")
        m = int(m)
    if "S" in dur:
        s = int(dur.replace("S", ""))
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


@router.get("/videos")
async def list_videos(sort: str = "date"):
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        videos = await asyncio.to_thread(client.list_videos, 200)

        result = []
        for v in videos:
            thumb = v["snippet"].get("thumbnails", {}).get("default", {}).get("url", "")
            result.append({
                "id": v["id"],
                "title": v["snippet"]["title"],
                "description": v["snippet"].get("description", ""),
                "tags": v["snippet"].get("tags", []),
                "thumbnail": thumb,
                "views": int(v["statistics"].get("viewCount", 0)),
                "likes": int(v["statistics"].get("likeCount", 0)),
                "duration": _parse_duration(v["contentDetails"]["duration"]),
                "published": v["snippet"]["publishedAt"][:10],
            })

        if sort == "views":
            result.sort(key=lambda x: x["views"], reverse=True)
        elif sort == "title":
            result.sort(key=lambda x: x["title"].lower())

        return {"videos": result}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.put("/videos/{video_id}")
async def update_video(video_id: str, body: VideoUpdate):
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        await asyncio.to_thread(
            client.update_video,
            video_id,
            title=body.title,
            description=body.description,
            tags=body.tags,
        )
        return {"message": "Video updated"}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@router.delete("/videos/{video_id}")
async def delete_video(video_id: str):
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        await asyncio.to_thread(client.delete_video, video_id)
        return {"message": "Video deleted"}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@router.post("/videos/{video_id}/thumbnail")
async def upload_thumbnail(video_id: str, file: UploadFile = File(...)):
    import tempfile
    import os
    try:
        from app import get_yt_client
        # Save uploaded file to temp location
        suffix = os.path.splitext(file.filename or ".jpg")[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        client = await asyncio.to_thread(get_yt_client)
        await asyncio.to_thread(client.set_thumbnail, video_id, tmp_path)
        os.unlink(tmp_path)
        return {"message": "Thumbnail uploaded"}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@router.post("/videos/bulk-action")
async def bulk_action(body: BulkAction):
    if body.action != "delete":
        return JSONResponse({"detail": f"Unknown action: {body.action}"}, status_code=400)
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        deleted = 0
        for vid in body.video_ids:
            await asyncio.to_thread(client.delete_video, vid)
            deleted += 1
        return {"message": f"{deleted} videos deleted"}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@router.get("/videos/thumbnail-priorities")
async def thumbnail_priorities():
    """Rank videos by thumbnail upgrade priority using analytics data."""
    try:
        from app import get_yt_client
        from datetime import date, timedelta
        client = await asyncio.to_thread(get_yt_client)
        end = date.today()
        start = end - timedelta(days=28)

        data = await asyncio.to_thread(
            client.get_video_impressions,
            str(start), str(end)
        )

        if not data.get("rows"):
            return {"priorities": []}

        # Calculate channel average CTR
        total_impressions = sum(r[2] for r in data["rows"] if r[2] > 0)
        total_views = sum(r[1] for r in data["rows"])
        avg_ctr = (total_views / total_impressions * 100) if total_impressions else 4.0

        priorities = []
        for row in data["rows"]:
            video_id, views, impressions, ctr, avg_dur = row[0], row[1], row[2], row[3], row[4]
            if impressions < 100:
                continue
            ctr_pct = round(ctr * 100, 2)
            ctr_gap = round(avg_ctr - ctr_pct, 2)
            impact = round(impressions * max(ctr_gap, 0) / 100)
            priorities.append({
                "video_id": video_id,
                "title": video_id,
                "impressions": impressions,
                "ctr": ctr_pct,
                "ctr_gap": ctr_gap,
                "impact_score": impact,
            })

        priorities.sort(key=lambda x: x["impact_score"], reverse=True)
        return {"priorities": priorities[:20]}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)
