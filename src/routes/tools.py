"""Content tools routes — title generator, transcript extractor, scripture cards, CSV export."""

import asyncio
import csv
import io
from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class TitleRequest(BaseModel):
    video_id: str


class ScriptureCardRequest(BaseModel):
    text: str
    card_type: str = "scripture"


@router.post("/api/tools/generate-titles")
async def generate_titles(body: TitleRequest):
    """Generate AI-optimized titles from video transcript."""
    try:
        # Try to get transcript
        transcript = await _get_transcript(body.video_id)
        if not transcript:
            return {"titles": [], "message": "No transcript available"}

        # Generate titles using keyword analysis
        titles = _generate_titles_from_transcript(transcript)
        return {"titles": titles}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@router.get("/api/tools/transcripts/{video_id}")
async def get_transcript(video_id: str):
    """Extract transcript for a video."""
    try:
        transcript = await _get_transcript(video_id)
        if transcript:
            return {"transcript": transcript}
        return {"transcript": None, "message": "No transcript available"}
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


@router.post("/api/tools/scripture-card")
async def generate_scripture_card(body: ScriptureCardRequest):
    """Generate a scripture card image via DALL-E."""
    import os
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {"image_url": None, "message": "OPENAI_API_KEY not set. Set it in .env to generate cards."}

    prompt = f"""Create a cinematic scripture card with:
- Deep navy/black background
- Bold gold serif text with subtle glow
- Text: "{body.text}"
- Style: {body.card_type} card
- Golden particles floating in background
- Dramatic chiaroscuro lighting
- Ancient scroll or stone tablet aesthetic
- NO human figures"""

    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        response = await asyncio.to_thread(
            lambda: client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",
                n=1,
            )
        )
        return {"image_url": response.data[0].url}
    except Exception as e:
        return {"image_url": None, "message": str(e)}


@router.get("/api/tools/export-csv")
async def export_csv():
    """Export all channel videos to CSV."""
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        videos = await asyncio.to_thread(client.list_videos, 300)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["video_id", "title", "published", "duration", "views", "likes", "comments", "tags"])

        for v in videos:
            writer.writerow([
                v["id"],
                v["snippet"]["title"],
                v["snippet"]["publishedAt"][:10],
                v["contentDetails"]["duration"],
                v["statistics"].get("viewCount", 0),
                v["statistics"].get("likeCount", 0),
                v["statistics"].get("commentCount", 0),
                "|".join(v["snippet"].get("tags", [])),
            ])

        csv_bytes = output.getvalue().encode("utf-8")
        return StreamingResponse(
            iter([csv_bytes]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=channel-videos.csv"},
        )
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)


# ── Helpers ──────────────────────────────────────────────────────────────

async def _get_transcript(video_id: str) -> Optional[str]:
    """Extract transcript using youtube_transcript_api if available."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        def _fetch():
            entries = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join(e["text"] for e in entries)

        return await asyncio.to_thread(_fetch)
    except ImportError:
        return None
    except Exception:
        return None


def _generate_titles_from_transcript(transcript: str) -> list[str]:
    """Generate title suggestions from transcript text using keyword analysis."""
    text_lower = transcript.lower()
    titles = []

    # Tribe detection
    tribes = {
        "judah": "Tribe of Judah", "benjamin": "Tribe of Benjamin",
        "levi": "Tribe of Levi", "simeon": "Tribe of Simeon",
        "ephraim": "Tribe of Ephraim", "manasseh": "Tribe of Manasseh",
        "gad": "Tribe of Gad", "reuben": "Tribe of Reuben",
        "naphtali": "Tribe of Naphtali", "zebulun": "Tribe of Zebulun",
        "issachar": "Tribe of Issachar", "asher": "Tribe of Asher",
    }

    found_tribes = [name for key, name in tribes.items() if key in text_lower]

    # Topic detection
    topics = {
        "scatter": "Scattered Among the Nations",
        "captiv": "The Captivity Fulfilled",
        "prophecy": "Prophecy Revealed",
        "curse": "The Curses of Deuteronomy 28",
        "restor": "The Restoration Is Coming",
        "identity": "The True Identity of Israel",
        "slave": "From Slavery to Prophecy",
        "awaken": "The Great Awakening",
    }

    found_topics = [desc for key, desc in topics.items() if key in text_lower]

    # Generate title combinations
    for tribe in found_tribes[:2]:
        for topic in found_topics[:2]:
            titles.append(f"{tribe} — {topic}")
        if not found_topics:
            titles.append(f"{tribe} — Who Are They Today?")

    for topic in found_topics[:3]:
        if not found_tribes:
            titles.append(f"The 12 Tribes of Israel — {topic}")

    if not titles:
        titles = [
            "The 12 Tribes of Israel — The Truth They Never Told You",
            "Deuteronomy 28 Fulfilled — See It for Yourself",
            "Biblical Prophecy Coming to Life Before Your Eyes",
        ]

    return titles[:5]
