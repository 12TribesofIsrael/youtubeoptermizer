"""
TikTok Studio analytics scraper — Playwright session reuse.

Pulls overview metrics (followers, profile views, video views, engagement)
plus per-video stats (views/likes/comments/shares/avg watch time) from
https://www.tiktok.com/tiktokstudio/analytics and writes CSVs to analytics/.

Subcommands:
    login    Interactive — opens a visible browser, you log in once, the
             session storage state is saved to .tiktok-session.json (gitignored).
             Cookies typically last ~30 days.

    scrape   Default — headless, reuses .tiktok-session.json. Writes:
                 analytics/tiktok-overview.csv      (appended each run)
                 analytics/tiktok-videos-{date}.csv (one file per scrape)

    debug    Saves analytics/_debug-overview.html + .png and
             analytics/_debug-content.html + .png so selectors can be
             refined against the live DOM. Run this first time the scrape
             returns empty rows.

Usage:
    python scripts/tiktok-analytics-scrape.py login
    python scripts/tiktok-analytics-scrape.py scrape
    python scripts/tiktok-analytics-scrape.py debug
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import (
    BrowserContext,
    Page,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    sync_playwright,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SESSION_FILE = REPO_ROOT / ".tiktok-session.json"
ANALYTICS_DIR = REPO_ROOT / "analytics"

OVERVIEW_URL = "https://www.tiktok.com/tiktokstudio/analytics/overview"
CONTENT_URL = "https://www.tiktok.com/tiktokstudio/analytics/content"
LOGIN_URL = "https://www.tiktok.com/login"

OVERVIEW_CSV = ANALYTICS_DIR / "tiktok-overview.csv"


# ── Section printing (matches scripts/tiktok-post.py style) ─────────────
def section(title: str) -> None:
    print()
    print("=" * 64)
    print(f"  {title}")
    print("=" * 64)


# ── Login flow ──────────────────────────────────────────────────────────
def cmd_login() -> int:
    section("TikTok Studio login — interactive")
    print("  A browser window will open. Log in to your TikTok account")
    print("  (the one connected to TikTok Studio for @aibiblegospels).")
    print("  Once you see the Studio dashboard, return to this terminal")
    print("  and press Enter. Session cookies will be saved.")
    print()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        page.goto(LOGIN_URL)
        input("  Press Enter here once you're logged in and on TikTok Studio...")

        # Verify login worked by hitting the analytics page
        page.goto(OVERVIEW_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        if "/login" in page.url:
            print("  Looks like login didn't take — current URL is the login page.")
            print("  Try again, and confirm the dashboard loads before pressing Enter.")
            browser.close()
            return 1

        context.storage_state(path=str(SESSION_FILE))
        print(f"\n  Session saved to {SESSION_FILE.relative_to(REPO_ROOT)}")
        browser.close()

    return 0


# ── Context helpers ─────────────────────────────────────────────────────
def open_authenticated_context(pw: Playwright, headless: bool) -> tuple[BrowserContext, "Browser"]:
    if not SESSION_FILE.exists():
        raise SystemExit(
            f"  No session file found at {SESSION_FILE}.\n"
            "  Run: python scripts/tiktok-analytics-scrape.py login"
        )
    browser = pw.chromium.launch(headless=headless)
    context = browser.new_context(
        viewport={"width": 1440, "height": 900},
        storage_state=str(SESSION_FILE),
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Safari/537.36"
        ),
    )
    return context, browser


def assert_logged_in(page: Page) -> None:
    if "/login" in page.url or "/passport" in page.url:
        raise SystemExit(
            "  Session expired — TikTok bounced us to the login page.\n"
            "  Re-run: python scripts/tiktok-analytics-scrape.py login"
        )


# ── Number parsing (TikTok displays "1.2K", "5,549", "3.4M") ───────────
def parse_metric(raw: str | None) -> float | None:
    if raw is None:
        return None
    s = raw.strip().replace(",", "").replace(" ", "")
    if not s or s == "-":
        return None
    m = re.match(r"^([\d.]+)\s*([KMB])?$", s, re.IGNORECASE)
    if not m:
        # might be a percentage like "12.3%"
        pct = re.match(r"^([\d.]+)\s*%$", s)
        if pct:
            return float(pct.group(1))
        return None
    n = float(m.group(1))
    suffix = (m.group(2) or "").upper()
    return n * {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}.get(suffix, 1)


# ── Overview extraction ────────────────────────────────────────────────
# Strategy: pull every visible card label/value pair on the overview page,
# then map well-known labels to columns. Keys we don't expect get logged
# but ignored — keeps us resilient to TikTok adding new cards.
KNOWN_OVERVIEW_LABELS = {
    "video views": "video_views",
    "profile views": "profile_views",
    "likes": "likes",
    "comments": "comments",
    "shares": "shares",
    "followers": "followers",
    "net followers": "net_followers",
    "engagement rate": "engagement_rate",
}


def scrape_overview(page: Page) -> dict[str, float | None]:
    page.goto(OVERVIEW_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    assert_logged_in(page)

    # TikTok Studio renders metric cards as label+value pairs. We grab
    # every element that looks like a heading and try to find an adjacent
    # number. JS in the page is faster and more robust than chained
    # locator queries here.
    pairs = page.evaluate(
        """() => {
            const out = [];
            const candidates = document.querySelectorAll(
                '[class*="metric"], [class*="Metric"], [class*="card"], [class*="Card"], [data-tt*="metric"]'
            );
            const seen = new Set();
            candidates.forEach(el => {
                const text = el.innerText || '';
                if (!text || seen.has(text)) return;
                seen.add(text);
                out.push(text);
            });
            return out;
        }"""
    )

    result: dict[str, float | None] = {k: None for k in KNOWN_OVERVIEW_LABELS.values()}
    for block in pairs:
        # Each block is multi-line: "Followers\n5,549\n+2.3%"
        lines = [ln.strip() for ln in block.split("\n") if ln.strip()]
        if len(lines) < 2:
            continue
        label = lines[0].lower().strip()
        col = KNOWN_OVERVIEW_LABELS.get(label)
        if not col:
            continue
        result[col] = parse_metric(lines[1])

    return result


# ── Content table extraction ───────────────────────────────────────────
def scrape_videos(page: Page) -> list[dict]:
    page.goto(CONTENT_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    assert_logged_in(page)

    # The content tab renders a table where each row is a video. Selectors
    # vary, so we walk every row-ish element and extract text + the first
    # video link found inside.
    rows = page.evaluate(
        """() => {
            const out = [];
            const rowEls = document.querySelectorAll(
                '[role="row"], [class*="VideoItem"], [class*="video-item"], [class*="ContentRow"]'
            );
            rowEls.forEach(row => {
                const link = row.querySelector('a[href*="/video/"]');
                if (!link) return;
                const href = link.href;
                const m = href.match(/\\/video\\/(\\d+)/);
                if (!m) return;
                const cells = Array.from(row.querySelectorAll('td, [role="cell"], [class*="cell"]'))
                    .map(c => (c.innerText || '').trim())
                    .filter(t => t.length > 0);
                out.push({ video_id: m[1], video_url: href, cells });
            });
            return out;
        }"""
    )

    # Dedupe by video_id (TikTok sometimes nests row matches)
    deduped: dict[str, dict] = {}
    for r in rows:
        deduped.setdefault(r["video_id"], r)

    # The cell order on the content tab (as of 2026): thumbnail/title,
    # posted_at, views, likes, comments, shares, avg_watch_time. We can't
    # rely on positions if TikTok changes columns, so we tag obvious ones
    # by shape: dates contain '/' or 'ago', durations contain ':',
    # percentages contain '%', and everything else is a count.
    out = []
    for video_id, r in deduped.items():
        cells: list[str] = r["cells"]
        record = {
            "video_id": video_id,
            "video_url": r["video_url"],
            "title": cells[0] if cells else "",
            "posted_at": "",
            "views": None,
            "likes": None,
            "comments": None,
            "shares": None,
            "avg_watch_time": "",
            "completion_rate": None,
            "raw_cells": " | ".join(cells),
        }
        numerics: list[float] = []
        for c in cells[1:]:
            if "ago" in c.lower() or re.search(r"\d{1,2}/\d{1,2}", c):
                record["posted_at"] = c
            elif ":" in c and re.match(r"^\d+:\d+", c):
                record["avg_watch_time"] = c
            elif c.endswith("%"):
                record["completion_rate"] = parse_metric(c)
            else:
                v = parse_metric(c)
                if v is not None:
                    numerics.append(v)
        # Map first 4 numerics positionally to views/likes/comments/shares
        for col, val in zip(
            ("views", "likes", "comments", "shares"),
            numerics[:4],
        ):
            record[col] = val
        out.append(record)

    return out


# ── CSV writers ────────────────────────────────────────────────────────
def write_overview(scraped_at: str, data: dict) -> Path:
    ANALYTICS_DIR.mkdir(exist_ok=True)
    fieldnames = ["scraped_at"] + list(KNOWN_OVERVIEW_LABELS.values())
    is_new = not OVERVIEW_CSV.exists()
    with OVERVIEW_CSV.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if is_new:
            w.writeheader()
        w.writerow({"scraped_at": scraped_at, **data})
    return OVERVIEW_CSV


def write_videos(scraped_at: str, rows: list[dict]) -> Path:
    ANALYTICS_DIR.mkdir(exist_ok=True)
    date = scraped_at[:10]
    out_path = ANALYTICS_DIR / f"tiktok-videos-{date}.csv"
    fieldnames = [
        "scraped_at", "video_id", "video_url", "title", "posted_at",
        "views", "likes", "comments", "shares",
        "avg_watch_time", "completion_rate", "raw_cells",
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({"scraped_at": scraped_at, **r})
    return out_path


# ── Main scrape command ────────────────────────────────────────────────
def cmd_scrape(headless: bool = True) -> int:
    section("TikTok Studio scrape")
    scraped_at = dt.datetime.now().isoformat(timespec="seconds")

    with sync_playwright() as pw:
        context, browser = open_authenticated_context(pw, headless=headless)
        page = context.new_page()

        print("  Loading overview...")
        overview = scrape_overview(page)
        for k, v in overview.items():
            print(f"    {k:18s} = {v}")
        out1 = write_overview(scraped_at, overview)
        print(f"  Wrote {out1.relative_to(REPO_ROOT)}")

        print("\n  Loading content table...")
        videos = scrape_videos(page)
        print(f"  Found {len(videos)} videos")
        out2 = write_videos(scraped_at, videos)
        print(f"  Wrote {out2.relative_to(REPO_ROOT)}")

        browser.close()

    if not videos or all(v.get("views") is None for v in videos):
        print()
        print("  WARNING: video rows look empty or unparsed.")
        print("  Run: python scripts/tiktok-analytics-scrape.py debug")
        print("  Then share the saved HTML so the selectors can be refined.")

    return 0


# ── Debug command — dumps DOM + screenshot for selector tuning ─────────
def cmd_debug() -> int:
    section("TikTok Studio debug dump")
    ANALYTICS_DIR.mkdir(exist_ok=True)

    with sync_playwright() as pw:
        context, browser = open_authenticated_context(pw, headless=True)
        page = context.new_page()

        for name, url in (("overview", OVERVIEW_URL), ("content", CONTENT_URL)):
            print(f"  Loading {name}...")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45_000)
            except PlaywrightTimeoutError:
                print(f"    timeout loading {url}")
                continue
            page.wait_for_timeout(6000)
            assert_logged_in(page)
            html_path = ANALYTICS_DIR / f"_debug-{name}.html"
            png_path = ANALYTICS_DIR / f"_debug-{name}.png"
            html_path.write_text(page.content(), encoding="utf-8")
            page.screenshot(path=str(png_path), full_page=True)
            print(f"    wrote {html_path.relative_to(REPO_ROOT)}")
            print(f"    wrote {png_path.relative_to(REPO_ROOT)}")

        browser.close()

    return 0


# ── Entrypoint ─────────────────────────────────────────────────────────
def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    cmd = argv[0]
    if cmd == "login":
        return cmd_login()
    if cmd == "scrape":
        headed = "--headed" in argv
        return cmd_scrape(headless=not headed)
    if cmd == "debug":
        return cmd_debug()
    print(f"  Unknown command: {cmd}")
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
