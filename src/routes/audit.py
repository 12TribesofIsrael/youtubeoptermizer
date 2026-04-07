"""Audit routes — social media audit (Claude AI) and channel health audit."""

import os
import re
import asyncio
from datetime import date
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import markdown

router = APIRouter()


def _load_system_prompt() -> str:
    from pathlib import Path
    paths = [
        Path(__file__).resolve().parent.parent.parent / ".claude" / "skills" / "social-media-audit" / "SKILL.md",
        Path.home() / ".claude" / "skills" / "social-media-audit" / "SKILL.md",
    ]
    skill_content = ""
    for p in paths:
        if p.exists():
            skill_content = p.read_text(encoding="utf-8")
            break

    return f"""You are a social media audit expert. Today's date is {date.today().isoformat()}.

{skill_content}

IMPORTANT INSTRUCTIONS FOR THIS WEB APP CONTEXT:
- You are generating the audit report directly — do NOT reference "sub-agents" or "Phase 2 research agents".
- Generate the COMPLETE audit report in markdown format.
- Be thorough — cover every platform the user provided.
- Include copy-paste bios with exact character counts.
- Make every recommendation actionable with specific numbers, copy, and steps.
"""


def _parse_platforms(social_urls: str) -> list[str]:
    platforms = []
    url_lower = social_urls.lower()
    if "instagram" in url_lower or "ig" in url_lower:
        platforms.append("Instagram")
    if "tiktok" in url_lower:
        platforms.append("TikTok")
    if "twitter" in url_lower or "x.com" in url_lower:
        platforms.append("X/Twitter")
    if "facebook" in url_lower or "fb.com" in url_lower:
        platforms.append("Facebook")
    if "linkedin" in url_lower:
        platforms.append("LinkedIn")
    return platforms or ["Instagram", "TikTok", "X/Twitter", "Facebook"]


@router.post("/api/audit/social")
async def run_social_audit(
    youtube_handle: str = Form(...),
    social_urls: str = Form(...),
    niche: str = Form(""),
    competitor: str = Form(""),
):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set")

    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    niche = niche or "general content creation"
    platforms = _parse_platforms(social_urls)
    platform_list = ", ".join(platforms)

    # 3 parallel research prompts
    prompts = [
        f"Research current (2026) social media best practices for: {platform_list}. For EACH platform provide optimal bio length, posting frequency, best times (EST), content formats, hashtag strategy, algorithm tips. Niche: \"{niche}\".",
        f"Find a top creator in \"{niche}\" niche on {platform_list}. {'Research: ' + competitor if competitor else 'Find someone 10K-500K followers.'}. Analyze bio, frequency, formats, hashtags, engagement tactics.",
        f"Research trending hashtags and content strategies for \"{niche}\" niche across {platform_list}. Find core, sub-niche, platform-specific, and trending hashtags. Content format recommendations.",
    ]

    async def _call(prompt):
        def _sync():
            return client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            ).content[0].text
        return await asyncio.to_thread(_sync)

    research = await asyncio.gather(*[_call(p) for p in prompts])

    system_prompt = _load_system_prompt()
    report_prompt = f"""Generate a COMPLETE social media audit report.

## Client Info
- **YouTube:** {youtube_handle}
- **Social Profiles:** {social_urls}
- **Niche:** {niche}
- **Competitor:** {competitor or "Find one based on research"}

## Research: Best Practices
{research[0]}

## Research: Competitor
{research[1]}

## Research: Hashtags
{research[2]}

Generate the full audit in markdown with: Quick Reference table, Competitor Benchmark, per-platform sections, Bio Templates, Cross-Posting Workflow, Priority Action List, Hashtag Bank, Key Metrics."""

    def _report():
        return client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": report_prompt}],
        ).content[0].text

    report_md = await asyncio.to_thread(_report)
    report_html = markdown.markdown(report_md, extensions=["tables", "fenced_code", "codehilite", "toc"])
    return {"markdown": report_md, "html": report_html}


@router.post("/api/audit/download-pdf")
async def download_pdf(request: Request):
    body = await request.json()
    report_html = body.get("html", "")
    if not report_html:
        raise HTTPException(status_code=400, detail="No report HTML provided")

    styled_html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
body {{ font-family: 'Segoe UI', sans-serif; padding: 40px; color: #1a1a1a; line-height: 1.6; }}
h1 {{ color: #0a0e1a; border-bottom: 3px solid #d4a843; padding-bottom: 10px; }}
h2 {{ color: #1a1a2e; margin-top: 30px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
th {{ background: #0a0e1a; color: #d4a843; }}
pre {{ background: #1a1a2e; color: #d4a843; padding: 15px; border-radius: 8px; }}
</style></head><body>{report_html}
<hr><p style="text-align:center;color:#999;font-size:0.85em">Generated by YouTube Optimizer | {date.today().isoformat()}</p>
</body></html>"""

    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=styled_html).write_pdf()
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=social-media-audit.pdf"},
        )
    except ImportError:
        raise HTTPException(status_code=500, detail="WeasyPrint not installed")


@router.post("/api/audit/channel")
async def run_channel_audit():
    """Run a full channel audit — categorize video issues."""
    try:
        from app import get_yt_client
        client = await asyncio.to_thread(get_yt_client)
        videos = await asyncio.to_thread(client.list_videos, 300)

        handle_in_title = []
        part_numbered = []
        very_short = []
        low_views = []
        matthew6_flood = []

        for v in videos:
            vid = v["id"]
            title = v["snippet"]["title"]
            views = int(v["statistics"].get("viewCount", 0))
            dur_iso = v["contentDetails"]["duration"]

            # Parse duration
            dur = dur_iso.replace("PT", "")
            seconds = 0
            if "H" in dur:
                h, dur = dur.split("H")
                seconds += int(h) * 3600
            if "M" in dur:
                m, dur = dur.split("M")
                seconds += int(m) * 60
            if "S" in dur:
                seconds += int(dur.replace("S", ""))

            entry = {"id": vid, "title": title, "views": views, "duration_sec": seconds}

            if "@aibiblegospels" in title.lower():
                handle_in_title.append(entry)
            if "Part " in title and ":" in title:
                part_numbered.append(entry)
            if 0 < seconds < 15:
                very_short.append(entry)
            if views < 30:
                low_views.append(entry)
            if "Matthew 6" in title:
                matthew6_flood.append(entry)

        return {
            "total_videos": len(videos),
            "handle_in_title": handle_in_title,
            "part_numbered": part_numbered,
            "very_short": very_short,
            "low_views": low_views,
            "matthew6_flood": matthew6_flood,
        }
    except Exception as e:
        return JSONResponse({"detail": str(e)}, status_code=500)
