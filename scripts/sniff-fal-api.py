"""
Sniff the API calls fal.ai's dashboard makes when loading recent-history.

Opens the dashboard under the persistent profile, captures every XHR/fetch
request, prints URL + response status. Lets us reverse-engineer the actual
API endpoint behind the dashboard so we can call it directly for bulk
enumeration.

Usage:
  python scripts/sniff-fal-api.py
"""

import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

PROFILE_DIR = Path.home() / ".meta-playwright-profile"
HISTORY_URL = "https://fal.ai/dashboard/recent-history"
OUT = Path(__file__).resolve().parent.parent / "training" / "fal-api-sniff.json"


def main():
    captured = []
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            viewport={"width": 1400, "height": 900},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        def on_request(req):
            # Filter to API-ish hosts only (skip CDN / static)
            if any(h in req.url for h in ("/api/", "api.fal", "queue.fal", "rest.alpha.fal", "_next/data")):
                captured.append({
                    "url": req.url,
                    "method": req.method,
                    "resource_type": req.resource_type,
                    "headers": dict(req.headers),
                })

        page.on("request", on_request)

        print(f"Navigating to {HISTORY_URL} ...")
        page.goto(HISTORY_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(8)  # let XHR finish

        # Scroll once to trigger any lazy-load
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)

        # Try clicking anything that looks like a button — captures pagination requests
        # if there are any.
        buttons = page.locator("button").all()
        print(f"  Found {len(buttons)} buttons on page")

        ctx.close()

    OUT.write_text(json.dumps(captured, indent=2), encoding="utf-8")
    print(f"\nCaptured {len(captured)} API calls -> {OUT}")
    print()
    # Print compact summary
    seen_urls = {}
    for c in captured:
        # Strip query params for grouping
        base = c["url"].split("?")[0]
        seen_urls[base] = seen_urls.get(base, 0) + 1
    print("Unique API endpoints hit (with hit count):")
    for url, count in sorted(seen_urls.items(), key=lambda x: -x[1]):
        print(f"  {count:>3}  {url}")


if __name__ == "__main__":
    main()
