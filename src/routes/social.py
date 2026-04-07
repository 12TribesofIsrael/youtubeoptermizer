"""Social media routes — post composer, caption manager, templates."""

import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# Import social modules
from src.social.facebook import POSTS as FB_POSTS, build_post_message, post_to_facebook
from src.social.twitter import TWEETS, post_tweet as _post_tweet
from src.social.caption_cleaner import clean_message


LINKTREE = "https://linktr.ee/aibiblegospels"
YOUTUBE_URL = "https://www.youtube.com/@AIBIBLEGOSPELS"


class PostRequest(BaseModel):
    platform: str
    content: str
    live: bool = False


@router.get("/api/social/templates/{platform}")
async def get_templates(platform: str):
    if platform == "facebook":
        return {
            "templates": [
                {
                    "type": t["type"],
                    "preview": build_post_message(t, YOUTUBE_URL),
                }
                for t in FB_POSTS
            ]
        }
    elif platform == "twitter":
        return {
            "templates": [
                {
                    "type": t["type"],
                    "preview": t["text"].replace("{link}", LINKTREE),
                }
                for t in TWEETS
            ]
        }
    return JSONResponse({"detail": f"Unknown platform: {platform}"}, status_code=400)


@router.post("/api/social/post")
async def publish_post(body: PostRequest):
    import asyncio

    if body.platform == "facebook":
        result = await asyncio.to_thread(post_to_facebook, body.content, None, not body.live)
        if "error" in result:
            return JSONResponse({"detail": str(result["error"])}, status_code=500)
        mode = "LIVE" if body.live else "DRY RUN"
        return {"message": f"Facebook post {mode} — ID: {result.get('id', 'N/A')}"}

    elif body.platform == "twitter":
        if not body.live:
            return {"message": f"Twitter DRY RUN — {len(body.content)} chars"}
        result = await asyncio.to_thread(_post_tweet, body.content)
        if "error" in result:
            return JSONResponse({"detail": str(result["error"])}, status_code=500)
        tweet_id = result.get("data", {}).get("id", "")
        return {"message": f"Tweet posted — ID: {tweet_id}"}

    return JSONResponse({"detail": f"Unknown platform: {body.platform}"}, status_code=400)


@router.get("/api/social/posts/{platform}")
async def get_existing_posts(platform: str):
    import asyncio
    if platform == "facebook":
        from src.social.meta_updater import get_facebook_posts
        posts = await asyncio.to_thread(get_facebook_posts, 50)
        return {
            "posts": [
                {
                    "id": p["id"],
                    "message": p.get("message", ""),
                    "date": p.get("created_time", "")[:10],
                }
                for p in posts
            ]
        }
    return JSONResponse({"detail": "Only Facebook supported currently"}, status_code=400)


@router.put("/api/social/posts/{platform}/{post_id}")
async def update_post(platform: str, post_id: str):
    import asyncio
    if platform == "facebook":
        from src.social.meta_updater import build_viral_caption, get_facebook_posts
        # Find original post
        posts = await asyncio.to_thread(get_facebook_posts, 100)
        original = next((p for p in posts if p["id"] == post_id), None)
        if not original:
            return JSONResponse({"detail": "Post not found"}, status_code=404)
        new_caption = build_viral_caption(original.get("message", ""), "facebook", post_id)
        return {"message": "Caption enhanced (dry run)", "preview": new_caption[:200]}
    return JSONResponse({"detail": "Only Facebook supported"}, status_code=400)


@router.post("/api/social/captions/clean")
async def clean_captions():
    import asyncio
    from src.social.meta_updater import get_facebook_posts
    posts = await asyncio.to_thread(get_facebook_posts, 100)
    dirty = 0
    for p in posts:
        msg = p.get("message", "")
        cleaned = clean_message(msg)
        if cleaned is not None:
            dirty += 1
    return {
        "message": f"Found {dirty} posts with Repurpose.io garbage (dry run — no changes made)",
        "dirty_count": dirty,
        "total": len(posts),
    }
