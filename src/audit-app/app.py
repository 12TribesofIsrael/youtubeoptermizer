"""
Social Media Audit SaaS — FastAPI Backend
Generates comprehensive social media audit reports using Claude API.

Usage:
    set ANTHROPIC_API_KEY=your-key
    cd src/audit-app
    pip install -r requirements.txt
    uvicorn app:app --reload --port 8000
"""

import os
import asyncio
import json
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import anthropic
import markdown

app = FastAPI(title="Social Media Audit Tool")
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

SKILL_PATH = Path(__file__).resolve().parent.parent.parent / ".claude" / "skills" / "social-media-audit" / "SKILL.md"

# ── System prompt built from the skill file ──────────────────────────────
def load_system_prompt() -> str:
    """Load the SKILL.md and convert it to a system prompt for Claude."""
    # Try project-level first, then user-level
    paths = [
        SKILL_PATH,
        Path.home() / ".claude" / "skills" / "social-media-audit" / "SKILL.md",
    ]
    skill_content = None
    for p in paths:
        if p.exists():
            skill_content = p.read_text(encoding="utf-8")
            break

    if not skill_content:
        # Inline fallback — core instructions
        skill_content = ""

    return f"""You are a social media audit expert. Today's date is {date.today().isoformat()}.

{skill_content}

IMPORTANT INSTRUCTIONS FOR THIS WEB APP CONTEXT:
- You are generating the audit report directly — do NOT reference "sub-agents" or "Phase 2 research agents" since you are the single model generating everything.
- Instead of launching agents, YOU do all the research and analysis yourself in one pass.
- Do NOT ask the user questions — you have all the info you need from the form inputs.
- Generate the COMPLETE audit report in markdown format.
- Be thorough — cover every platform the user provided.
- Include copy-paste bios with exact character counts.
- Include a competitor benchmark section even if no competitor was provided (find/suggest one).
- Make every recommendation actionable with specific numbers, copy, and steps.
"""


# ── Research prompts for parallel Claude calls ───────────────────────────
def build_research_prompts(youtube_handle: str, social_urls: str, niche: str, competitor: str):
    """Build 3 research prompts that run in parallel."""
    platforms = parse_platforms(social_urls)
    platform_list = ", ".join(platforms) if platforms else "Instagram, TikTok, X, Facebook"

    prompt_best_practices = f"""Research current (2026) social media best practices for these platforms: {platform_list}.

For EACH platform, provide:
- Optimal bio length and what high-performing accounts include
- Ideal posting frequency for a solo creator
- Best times to post (EST)
- Content formats that perform best right now (Reels, carousels, threads, lives, etc.)
- Current hashtag strategy (how many to use, mix of broad/niche)
- Algorithm tips and recent changes
- How to optimize specifically for driving traffic to YouTube
- Profile pic and banner dimensions
- Account type recommendations (Business vs Creator vs Personal)

Be specific with numbers and examples. This is for a creator in the "{niche}" niche."""

    prompt_competitor = f"""Find a top-performing creator in the "{niche}" niche who is active on {platform_list}.
{"The user suggested this competitor: " + competitor + ". Research their social profiles." if competitor else "Find someone with 10K-500K followers who is doing social media well — not a mega-influencer, someone comparable but ahead."}

Analyze:
- Their bio copy on each platform
- Content frequency (how often do they post?)
- Content formats they use
- Hashtag strategy
- Cross-platform consistency
- Engagement tactics (CTAs, pinned posts, stories)
- What they do that a smaller creator likely doesn't
- What's working well for them

Return a structured competitor profile."""

    prompt_hashtags = f"""Research trending hashtags and content strategies for the "{niche}" niche across {platform_list}.

Find:
1. Core hashtags (5-7) — evergreen, always relevant
2. Sub-niche hashtags (8-10) — specific topics within the niche
3. Platform-specific hashtags (e.g., #bibletok for TikTok)
4. Trending hashtags (5-7) — currently popular, rotate weekly
5. Content formats winning right now in this niche:
   - What types of carousels/threads/Reels get the most saves and shares?
   - Are duets/stitches working?
   - Are lives or Q&As driving engagement?
   - Content gaps — what are creators NOT doing that they should?

Return organized by category with specific hashtag recommendations."""

    return prompt_best_practices, prompt_competitor, prompt_hashtags


def parse_platforms(social_urls: str) -> list[str]:
    """Extract platform names from URLs."""
    platforms = []
    url_lower = social_urls.lower()
    if "instagram" in url_lower or "ig" in url_lower:
        platforms.append("Instagram")
    if "tiktok" in url_lower:
        platforms.append("TikTok")
    if "twitter" in url_lower or "/x.com" in url_lower or "x.com" in url_lower:
        platforms.append("X/Twitter")
    if "facebook" in url_lower or "fb.com" in url_lower:
        platforms.append("Facebook")
    if "linkedin" in url_lower:
        platforms.append("LinkedIn")
    if "threads" in url_lower:
        platforms.append("Threads")
    if not platforms:
        platforms = ["Instagram", "TikTok", "X/Twitter", "Facebook"]
    return platforms


# ── API Routes ───────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/audit")
async def run_audit(
    youtube_handle: str = Form(...),
    social_urls: str = Form(...),
    niche: str = Form(""),
    competitor: str = Form(""),
):
    """Run the 3-phase audit and return the markdown report."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set")

    client = anthropic.Anthropic(api_key=api_key)
    niche = niche or "general content creation"

    # Phase 2: Run 3 research prompts in parallel using asyncio
    p1, p2, p3 = build_research_prompts(youtube_handle, social_urls, niche, competitor)

    async def call_claude(prompt: str, label: str) -> str:
        """Call Claude API (sync client wrapped in thread)."""
        def _call():
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text
        return await asyncio.to_thread(_call)

    # Run all 3 research calls in parallel
    research_results = await asyncio.gather(
        call_claude(p1, "best_practices"),
        call_claude(p2, "competitor"),
        call_claude(p3, "hashtags"),
    )

    best_practices, competitor_analysis, hashtag_research = research_results

    # Phase 3: Generate the full report using all research
    system_prompt = load_system_prompt()

    report_prompt = f"""Generate a COMPLETE social media audit report using the research below.

## Client Info
- **YouTube:** {youtube_handle}
- **Social Profiles:** {social_urls}
- **Niche:** {niche}
- **Competitor:** {competitor if competitor else "Find/suggest one based on the research"}
- **Date:** {date.today().isoformat()}

## Research: Platform Best Practices
{best_practices}

## Research: Competitor Analysis
{competitor_analysis}

## Research: Hashtag & Content Trends
{hashtag_research}

Now generate the full audit report in markdown following the template structure in your instructions. Include:
1. Quick Reference table with profile specs
2. Competitor Benchmark section
3. Per-platform sections (Profile Setup, Copy-Paste Bio, Content Strategy, Competitor Comparison, Fixes Checklist)
4. Universal Bio Templates (full/medium/short)
5. Cross-Posting Workflow table
6. Profile Picture & Banner Consistency
7. Priority Action List (Immediate / This Week / This Month)
8. Hashtag Bank (organized by category)
9. Key Metrics to Track Monthly

Make every bio copy-paste ready in code blocks with character counts verified."""

    def _generate_report():
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": report_prompt}],
        )
        return resp.content[0].text

    report_md = await asyncio.to_thread(_generate_report)

    # Convert markdown to HTML
    report_html = markdown.markdown(
        report_md,
        extensions=["tables", "fenced_code", "codehilite", "toc"],
    )

    return {"markdown": report_md, "html": report_html}


@app.post("/download-pdf")
async def download_pdf(request: Request):
    """Convert the markdown report to PDF for download."""
    body = await request.json()
    report_html = body.get("html", "")

    if not report_html:
        raise HTTPException(status_code=400, detail="No report HTML provided")

    # Build a styled HTML document for PDF
    styled_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; padding: 40px; color: #1a1a1a; line-height: 1.6; }}
    h1 {{ color: #0a0e1a; border-bottom: 3px solid #d4a843; padding-bottom: 10px; }}
    h2 {{ color: #1a1a2e; margin-top: 30px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
    h3 {{ color: #333; }}
    table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
    th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
    th {{ background: #0a0e1a; color: #d4a843; }}
    code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }}
    pre {{ background: #1a1a2e; color: #d4a843; padding: 15px; border-radius: 8px; overflow-x: auto; }}
    pre code {{ background: none; color: inherit; }}
    ul {{ padding-left: 20px; }}
    li {{ margin: 4px 0; }}
    .priority-high {{ color: #e74c3c; font-weight: bold; }}
    .priority-medium {{ color: #f39c12; font-weight: bold; }}
    .priority-low {{ color: #27ae60; font-weight: bold; }}
</style>
</head>
<body>
{report_html}
<hr>
<p style="text-align: center; color: #999; font-size: 0.85em;">
    Generated by Social Media Audit Tool | {date.today().isoformat()}
</p>
</body>
</html>"""

    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=styled_html).write_pdf()
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=social-media-audit.pdf"},
        )
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="WeasyPrint not installed. Install with: pip install weasyprint"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
