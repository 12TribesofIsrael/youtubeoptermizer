"""
Bulk-download FLUX renders + their prompts from fal.ai dashboard history.

Strategy (refined 2026-05-17 after the initial DOM-walk approach failed):
  1. Use Playwright to load fal.ai/dashboard/recent-history under the
     persistent profile (gets the SPA's rendered HTML with all the request
     hyperlinks).
  2. Parse out (app_id, request_id) pairs from the hrefs — each row links to
     /models/{app}/playground?requestId={id}.
  3. For each FLUX request, hit fal.ai's queue API directly to fetch the
     completed result (input prompt + output image URLs).
  4. Download images + write matching .txt caption files.

Faster than DOM-walking each playground detail page, and gets clean data
straight from the API instead of scraping rendered DOM.

For each downloaded entry:
  - {stem}-NN.jpg   → the rendered image
  - {stem}-NN.txt   → the prompt text (caption for LoRA training)

Usage:
  python scripts/scrape-fal-history.py
  python scripts/scrape-fal-history.py --max 200
  python scripts/scrape-fal-history.py --apps flux-pro,flux-pro/v1.1,flux-dev
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: pip install playwright && python -m playwright install chromium", file=sys.stderr)
    sys.exit(1)

# Reuse FAL_KEY from sibling repo if not set in this shell
if not os.getenv("FAL_KEY"):
    try:
        from dotenv import load_dotenv
        sibling_env = Path("C:/Users/Claude/ai-bible-gospels/.env")
        if sibling_env.exists():
            load_dotenv(sibling_env)
    except ImportError:
        pass

FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    print("ERROR: FAL_KEY not set. Source it from ai-bible-gospels/.env or shell.", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "training" / "lora-references"
PROFILE_DIR = Path.home() / ".meta-playwright-profile"
HISTORY_URL = "https://fal.ai/dashboard/recent-history"

# Match playground links: /models/{app}/playground?requestId={id}
# app is everything between /models/ and /playground (handles nested paths
# like fal-ai/flux-pro or fal-ai/flux-pro/v1.1-with-loras)
HREF_RE = re.compile(r'/models/([^"\?]+)/playground\?requestId=([0-9a-f-]+)')

FAL_QUEUE = "https://queue.fal.run"


def sanitize(text: str, max_len: int = 50) -> str:
    text = re.sub(r"[^\w\s-]", "", text).strip()
    text = re.sub(r"[-\s]+", "-", text)
    return text[:max_len] or "untitled"


def extract_requests_from_dashboard(headless: bool, page_pause: float, max_pages: int) -> list:
    """Load dashboard, paginate through all pages, collect (app, request_id) pairs.

    The dashboard uses explicit pagination ( '<' '>' chevron buttons ) — not lazy
    scroll loading. We extract requests from each page's HTML, then click the
    right chevron to advance until the button is missing/disabled.
    """
    print(f"Loading {HISTORY_URL} via Playwright...")
    seen = set()
    requests_found = []

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=headless,
            viewport={"width": 1400, "height": 900},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        page.goto(HISTORY_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)  # SPA hydration

        if "/auth" in page.url or "login" in page.url.lower():
            print(f"ERROR: redirected to login ({page.url}). Cookies expired.", file=sys.stderr)
            ctx.close()
            sys.exit(1)

        # Walk pagination — collect requests from each page, then click '>' to advance
        for page_num in range(1, max_pages + 1):
            html = page.content()
            before = len(seen)
            for match in HREF_RE.finditer(html):
                app = match.group(1)
                req_id = match.group(2)
                key = (app, req_id)
                if key in seen:
                    continue
                seen.add(key)
                requests_found.append({"app": app, "request_id": req_id})
            new_this_page = len(seen) - before
            print(f"  Page {page_num}: +{new_this_page} new requests (total: {len(seen)})")

            # If this page added zero new entries, we're likely looping — stop
            if new_this_page == 0 and page_num > 1:
                print(f"  Page {page_num} added zero new — stopping (likely looped or duplicated)")
                break

            # Locate the 'next page' button — try several common selector patterns
            next_btn = None
            selector_attempts = [
                'button[aria-label*="next" i]:not([disabled])',
                'button[aria-label*="Next" i]:not([disabled])',
                'a[aria-label*="next" i]:not([aria-disabled="true"])',
                # SVG chevron-right inside a button
                'button:has(svg.lucide-chevron-right):not([disabled])',
                # Last-resort: any button containing only a right-chevron character/glyph
                'button:has-text("›"):not([disabled])',
            ]
            for sel in selector_attempts:
                try:
                    locator = page.locator(sel)
                    if locator.count() > 0:
                        # Prefer the LAST matching one — pagination is usually at the bottom
                        next_btn = locator.last
                        break
                except Exception:
                    continue

            if not next_btn:
                # Save a debug HTML on the last page so we can iterate if pagination
                # detection is off
                debug_path = DEFAULT_OUT.parent / f"fal-history-page{page_num}-debug.html"
                debug_path.write_text(html, encoding="utf-8")
                print(f"  No 'next' button found on page {page_num}. Saved debug: {debug_path}")
                break

            try:
                next_btn.click(timeout=5000)
                time.sleep(page_pause)
            except Exception as e:
                print(f"  Failed to click next button on page {page_num}: {e}")
                break
        else:
            print(f"  Hit --max-pages={max_pages} cap")

        ctx.close()

    return requests_found


def fetch_request_result(app: str, request_id: str) -> dict:
    """GET a completed request's full payload from fal.ai queue API."""
    url = f"{FAL_QUEUE}/{app}/requests/{request_id}"
    resp = requests.get(
        url,
        headers={"Authorization": f"Key {FAL_KEY}"},
        timeout=30,
    )
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.json()


def extract_prompt_and_images(result: dict) -> tuple:
    """Best-effort extraction of (prompt, image_urls) from a queue result.

    fal.ai's queue API stores results in varied shapes per model. We probe
    common locations.
    """
    if not isinstance(result, dict):
        return "", []

    # The completed result usually wraps everything in a top-level dict.
    # FLUX results contain 'images' array of {url, content_type, ...}.
    images = []
    candidates = [result, result.get("response", {}), result.get("data", {})]
    for c in candidates:
        if not isinstance(c, dict):
            continue
        imgs = c.get("images")
        if isinstance(imgs, list):
            for img in imgs:
                if isinstance(img, dict) and "url" in img:
                    images.append(img["url"])
                elif isinstance(img, str):
                    images.append(img)
            if images:
                break

    # Prompt is usually in the request input
    prompt = ""
    for c in candidates:
        if not isinstance(c, dict):
            continue
        # Direct prompt field
        if c.get("prompt"):
            prompt = c["prompt"]
            break
        # Sometimes wrapped under 'input' or 'request'
        for key in ("input", "request", "params"):
            sub = c.get(key)
            if isinstance(sub, dict) and sub.get("prompt"):
                prompt = sub["prompt"]
                break
        if prompt:
            break

    return prompt, images


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--max", type=int, default=150,
                        help="Max images to download (default: 150)")
    parser.add_argument("--apps", default="flux-pro,flux-pro/v1.1,flux-pro/v1.1-with-loras,flux-dev,flux-lora",
                        help="Comma-separated app slugs to include (default: FLUX models only)")
    parser.add_argument("--all-apps", action="store_true",
                        help="Include ALL apps (Kling video frames, etc.) — usually leave off")
    parser.add_argument("--headless", action="store_true", default=True,
                        help="Run headless (default: True — visible window won't work in background subprocess)")
    parser.add_argument("--page-pause", type=float, default=2.0,
                        help="Seconds to wait after clicking next-page (default: 2.0)")
    parser.add_argument("--max-pages", type=int, default=50,
                        help="Max pages to paginate through (default: 50)")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output dir: {out_dir}")
    print(f"Max images: {args.max}")
    print()

    # Step 1 — get all (app, request_id) pairs from the dashboard, paginating
    all_requests = extract_requests_from_dashboard(
        args.headless, args.page_pause, args.max_pages
    )
    print(f"\nFound {len(all_requests)} total requests in dashboard history.")

    # Step 2 — filter to image-generating apps (FLUX) unless --all-apps
    if not args.all_apps:
        allowed = [a.strip() for a in args.apps.split(",")]
        # Match the trailing portion of the app slug (fal-ai/flux-pro -> flux-pro)
        def keep(app):
            tail = app.split("fal-ai/")[-1]
            return any(a in tail for a in allowed)
        filtered = [r for r in all_requests if keep(r["app"])]
        print(f"Filtered to {len(filtered)} FLUX-style requests "
              f"(use --all-apps to include Kling/etc.)")
        all_requests = filtered

    # Step 3 — fetch each request's output + prompt, download images
    existing_stems = {p.stem for p in out_dir.glob("*.jpg")}
    downloaded = 0
    skipped = 0
    api_errors = 0

    for i, req in enumerate(all_requests):
        if downloaded >= args.max:
            print(f"Hit --max={args.max} cap. Stopping.")
            break

        try:
            result = fetch_request_result(req["app"], req["request_id"])
        except Exception as e:
            api_errors += 1
            print(f"  [{i+1}] API err for {req['app']}/{req['request_id'][:8]}: {e}")
            continue

        if not result:
            api_errors += 1
            continue

        prompt, image_urls = extract_prompt_and_images(result)
        if not image_urls:
            continue

        # Use first image (FLUX typically returns 1)
        img_url = image_urls[0]
        first_words = " ".join(prompt.split()[:5]) if prompt else "untitled"
        stem = f"{sanitize(first_words)}-{i+1:03d}"

        if stem in existing_stems:
            skipped += 1
            continue

        img_path = out_dir / f"{stem}.jpg"
        txt_path = out_dir / f"{stem}.txt"

        try:
            r = requests.get(img_url, timeout=30)
            r.raise_for_status()
            img_path.write_bytes(r.content)
            if prompt:
                txt_path.write_text(prompt, encoding="utf-8")
            downloaded += 1
            if downloaded % 10 == 0:
                print(f"  Downloaded {downloaded} — last: {stem}")
        except Exception as e:
            print(f"  IMG fail {stem}: {e}")

    print()
    print(f"DONE — downloaded {downloaded}, skipped {skipped} dup, api errors {api_errors}")
    print(f"  Total in dashboard: {len(all_requests)}")
    print(f"  Output: {out_dir}")
    print()
    print("Next steps:")
    print("  1. Prune images you don't want (Caucasian/Greek/Edomite renders, bad outputs)")
    print("  2. Review .txt captions — standardize to 'aibgospels person, ...' format")
    print("  3. python scripts/train-flux-lora.py")


if __name__ == "__main__":
    main()
