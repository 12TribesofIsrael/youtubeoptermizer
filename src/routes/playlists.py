"""Playlist management routes."""

import asyncio
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()


class PlaylistCreate(BaseModel):
    title: str
    description: str = ""
    privacy: str = "public"


class PlaylistAddVideo(BaseModel):
    video_id: str


@router.get("/playlists")
async def list_playlists():
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        playlists = await asyncio.to_thread(client.list_playlists)
        return {
            "playlists": [
                {
                    "id": pl["id"],
                    "title": pl["snippet"]["title"],
                    "description": pl["snippet"].get("description", ""),
                    "video_count": pl["contentDetails"]["itemCount"],
                    "published": pl["snippet"]["publishedAt"][:10],
                }
                for pl in playlists
            ]
        }
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@router.post("/playlists")
async def create_playlist(body: PlaylistCreate):
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        result = await asyncio.to_thread(
            client.create_playlist, body.title, body.description, body.privacy
        )
        return {"message": "Playlist created", "id": result["id"]}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@router.post("/playlists/{playlist_id}/videos")
async def add_video(playlist_id: str, body: PlaylistAddVideo):
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        await asyncio.to_thread(client.add_to_playlist, playlist_id, body.video_id)
        return {"message": "Video added to playlist"}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@router.delete("/playlists/{playlist_id}/videos/{item_id}")
async def remove_video(playlist_id: str, item_id: str):
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        await asyncio.to_thread(client.remove_from_playlist, item_id)
        return {"message": "Video removed from playlist"}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)
