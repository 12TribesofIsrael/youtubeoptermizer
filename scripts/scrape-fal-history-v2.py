"""
Bulk-download fal.ai request history via the dashboard's tRPC endpoint.

Discovered 2026-05-17 via scripts/sniff-fal-api.py: the dashboard calls
`https://fal.ai/api/trpc/requests.search` with batched JSON params and
a cursor-paginated payload. Cookie-auth'd via the persistent Playwright
profile (no API-key auth available on this endpoint).

Strategy:
  1. Open Playwright with persistent profile so we inherit cookies.
  2. Use page.request.get() to call the tRPC endpoint with limit=100 +
     cursor pagination until results run out.
  3. Parse the tRPC response shape, extract request data (which usually
     includes input prompt + output image URLs directly).
  4. Download images + write matching caption .txt files.

Usage:
  python scripts/scrape-fal-history-v2.py
  python scripts/scrape-fal-history-v2.py --max 500 --limit 100
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests as py_requests
from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "training" / "lora-references"
PROFILE_DIR = Path.home() / ".meta-playwright-profile"
TRPC_BASE = "https://fal.ai/api/trpc/requests.search"


def build_trpc_url(limit: int, cursor: int, enable_bq: bool = False, endpoint: str = None) -> str:
    """Build the tRPC GET URL with batched JSON input.

    enable_bq=True flips the dashboard's BigQuery flag, which appears to
    unlock longer-term archived history beyond the recent-only view.

    endpoint filters to a specific fal.ai app slug like "fal-ai/flux-pro" —
    per-endpoint queries can expose older records than the aggregate view.
    """
    payload = {
        "0": {
            "json": {
                "searchQuery": None,
                "searchImageUrl": None,
                "searchVideoUrl": None,
                "limit": limit,
                "cursor": cursor,
                "enableBqTrpc": enable_bq,
                "endpoint": endpoint,
                "excludeApiRequests": None,
                "onlyApiRequests": None,
            },
            "meta": {
                "values": {
                    "searchQuery": ["undefined"],
                    "searchImageUrl": ["undefined"],
                    "searchVideoUrl": ["undefined"],
                    "excludeApiRequests": ["undefined"],
                    "onlyApiRequests": ["undefined"],
                },
            },
        }
    }
    # If endpoint is null (aggregate query), the dashboard sends it as "undefined"
    if endpoint is None:
        payload["0"]["meta"]["values"]["endpoint"] = ["undefined"]
    return f"{TRPC_BASE}?batch=1&input={quote(json.dumps(payload, separators=(',', ':')))}"


def parse_trpc_result(json_response):
    """Unwrap the tRPC batched response. Returns the data dict for batch index 0.

    tRPC batched response shape:
        [ { "result": { "data": { "json": {...actual data...} } } } ]
    """
    if not isinstance(json_response, list) or not json_response:
        return None
    item = json_response[0]
    if not isinstance(item, dict):
        return None
    result = item.get("result", {})
    data = result.get("data", {})
    if isinstance(data, dict):
        return data.get("json") or data
    return None


def sanitize(text: str, max_len: int = 50) -> str:
    text = re.sub(r"[^\w\s-]", "", text).strip()
    text = re.sub(r"[-\s]+", "-", text)
    return text[:max_len] or "untitled"


def extract_image_url(req_record):
    """Pull an image URL from a fal.ai dashboard record.

    Schema discovered 2026-05-17: records have json_input + json_output.
      FLUX requests:  json_output.images[0].url is the output image.
      Kling requests: json_input.image_url is the FLUX image that fed Kling.
        (Same image we generated earlier — useful for LoRA training too.)
    """
    if not isinstance(req_record, dict):
        return None
    out = req_record.get("json_output")
    if isinstance(out, dict):
        images = out.get("images")
        if isinstance(images, list) and images:
            img = images[0]
            if isinstance(img, dict) and isinstance(img.get("url"), str):
                return img["url"]
    # Kling input-image fallback
    inp = req_record.get("json_input")
    if isinstance(inp, dict):
        url = inp.get("image_url")
        if isinstance(url, str) and url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            return url
    return None


def extract_prompt(req_record):
    """Pull the FLUX prompt from a record's json_input."""
    if not isinstance(req_record, dict):
        return ""
    inp = req_record.get("json_input")
    if isinstance(inp, dict):
        return inp.get("prompt") or ""
    return ""


def is_flux_record(req_record):
    """Determine if this record is a FLUX request (or a Kling that consumed FLUX output)."""
    endpoint = (req_record.get("endpoint") or "").lower()
    if "flux" in endpoint:
        return True
    # Kling/video records reference a FLUX-generated image_url — still useful
    inp = req_record.get("json_input", {})
    if isinstance(inp, dict):
        url = inp.get("image_url") or ""
        if isinstance(url, str) and url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--max", type=int, default=300, help="Max images to download")
    parser.add_argument("--limit", type=int, default=100, help="Page size for tRPC (default 100)")
    parser.add_argument("--flux-only", action="store_true", default=True,
                        help="Filter to FLUX models (default True)")
    parser.add_argument("--all-apps", action="store_true",
                        help="Include all apps (Kling, etc.)")
    parser.add_argument("--save-raw", action="store_true",
                        help="Save raw tRPC responses to training/fal-trpc-raw.json")
    parser.add_argument("--bq", action="store_true",
                        help="Enable BigQuery flag in tRPC payload — unlocks deeper history")
    parser.add_argument("--per-endpoint", action="store_true",
                        help="After the aggregate scrape, also query each FLUX/Kling endpoint "
                             "individually — per-app history sometimes runs deeper")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    all_records = []
    raw_pages = []

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=True,
            viewport={"width": 1400, "height": 900},
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        # Visit dashboard once to ensure session cookies are warm
        page.goto("https://fal.ai/dashboard/recent-history", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)

        # Build the list of "queries" to run — aggregate first, then per-endpoint
        # if requested.
        queries = [None]  # aggregate (endpoint=None)
        if args.per_endpoint:
            # Endpoints we typically use — extend as needed
            queries.extend([
                "fal-ai/flux-pro/v1.1",
                "fal-ai/flux-pro/v1.1-with-loras",
                "fal-ai/flux-pro",
                "fal-ai/flux-dev",
                "fal-ai/flux-lora",
                "fal-ai/kling-video/v1.6/standard/image-to-video",
                "fal-ai/kling-video/v2.1/standard/image-to-video",
                "fal-ai/kling-video/v3/standard/image-to-video",
                "fal-ai/kling-video/o3/pro/image-to-video",
            ])

        seen_request_ids = set()
        for query_endpoint in queries:
            query_label = query_endpoint or "<aggregate>"
            print(f"\n=== Query: {query_label} ===")
            cursor = 0
            page_num = 0
            new_for_this_query = 0
            while True:
                page_num += 1
                url = build_trpc_url(args.limit, cursor, enable_bq=args.bq, endpoint=query_endpoint)
                print(f"  Page {page_num}: cursor={cursor}, limit={args.limit}, bq={args.bq}")
                # In-page fetch() to use the SPA's session cookies and avoid SSL issues
                body = page.evaluate(
                    """async (url) => {
                        const r = await fetch(url, { credentials: 'include' });
                        if (!r.ok) return { __error: true, status: r.status, text: await r.text() };
                        return await r.json();
                    }""",
                    url,
                )
                if isinstance(body, dict) and body.get("__error"):
                    print(f"    HTTP {body['status']}: {body['text'][:200]}")
                    break
                if args.save_raw:
                    raw_pages.append(body)

                data = parse_trpc_result(body)
                if not data:
                    print(f"    Unexpected tRPC shape — saving raw response for inspection")
                    raw_path = REPO_ROOT / "training" / f"fal-trpc-page{page_num}-debug.json"
                    raw_path.write_text(json.dumps(body, indent=2), encoding="utf-8")
                    print(f"    Saved: {raw_path}")
                    break

                records = (data.get("items") or data.get("requests") or
                           data.get("results") or data.get("data") or [])
                next_cursor = (data.get("nextCursor") if isinstance(data, dict) else None)

                if not records:
                    raw_path = REPO_ROOT / "training" / f"fal-trpc-page{page_num}-debug.json"
                    raw_path.write_text(json.dumps(data, indent=2)[:5000], encoding="utf-8")
                    print(f"    Zero records this page. Saved data shape: {raw_path}")
                    break

                # Dedupe by request_id across queries to avoid counting the same
                # request twice when it shows up in both aggregate + per-endpoint.
                new_records = [r for r in records
                               if r.get("request_id") not in seen_request_ids]
                for r in new_records:
                    seen_request_ids.add(r.get("request_id"))
                all_records.extend(new_records)
                new_for_this_query += len(new_records)
                print(f"    +{len(records)} records (+{len(new_records)} new, "
                      f"next_cursor={next_cursor})")

                if not next_cursor or next_cursor == cursor:
                    print(f"    No nextCursor — end of history")
                    break
                cursor = next_cursor
                if len(all_records) >= args.max * 3:
                    print(f"    Hit raw cap of {len(all_records)} records")
                    break
            print(f"  Query '{query_label}' contributed {new_for_this_query} new records")

        ctx.close()

    print(f"\nTotal records pulled: {len(all_records)}")

    if args.save_raw:
        raw_out = REPO_ROOT / "training" / "fal-trpc-raw.json"
        raw_out.write_text(json.dumps(raw_pages, indent=2), encoding="utf-8")
        print(f"Saved raw tRPC pages: {raw_out}")

    # First pass: build a url -> FLUX-prompt map from FLUX records.
    # FLUX records have json_output.images[0].url = the rendered image, and
    # json_input.prompt = the visual scene description. Kling records have a
    # `prompt` field too, but it's the MOTION instruction ("zoom-in", "slow pan
    # following the soldiers") — useless for LoRA training. So we always prefer
    # the FLUX prompt looked up by URL.
    url_to_flux_prompt = {}
    for r in all_records:
        endpoint = (r.get("endpoint") or "").lower()
        if "flux" not in endpoint:
            continue
        out = r.get("json_output", {})
        if not isinstance(out, dict):
            continue
        images = out.get("images")
        if not isinstance(images, list) or not images:
            continue
        url = images[0].get("url") if isinstance(images[0], dict) else None
        prompt = (r.get("json_input") or {}).get("prompt") or ""
        if url and prompt:
            url_to_flux_prompt[url] = prompt
    print(f"Built FLUX url->prompt map: {len(url_to_flux_prompt)} entries")

    if not args.all_apps:
        flux_records = [r for r in all_records if is_flux_record(r)]
        print(f"After FLUX filter (includes Kling-input FLUX images): {len(flux_records)}")
        all_records = flux_records

    # Dedupe by image URL — Kling input image_url can match a prior FLUX output
    seen_urls = set()
    deduped = []
    for r in all_records:
        url = extract_image_url(r)
        if url and url not in seen_urls:
            seen_urls.add(url)
            deduped.append(r)
    print(f"After URL dedup: {len(deduped)}")
    all_records = deduped

    # Download
    existing_stems = {p.stem for p in out_dir.glob("*.jpg")}
    downloaded = 0
    skipped = 0
    no_image = 0

    captions_from_flux_map = 0
    captions_from_kling = 0
    for i, rec in enumerate(all_records):
        if downloaded >= args.max:
            break
        img_url = extract_image_url(rec)
        if not img_url:
            no_image += 1
            continue
        # Prefer the FLUX visual prompt for this image URL; fall back to whatever
        # this record's own prompt field has (only useful for FLUX records).
        flux_prompt = url_to_flux_prompt.get(img_url)
        if flux_prompt:
            prompt = flux_prompt
            captions_from_flux_map += 1
        else:
            prompt = extract_prompt(rec)
            if prompt:
                captions_from_kling += 1
        first_words = " ".join(prompt.split()[:5]) if prompt else "untitled"
        stem = f"{sanitize(first_words)}-{i+1:04d}"
        if stem in existing_stems:
            skipped += 1
            continue

        img_path = out_dir / f"{stem}.jpg"
        txt_path = out_dir / f"{stem}.txt"
        try:
            r = py_requests.get(img_url, timeout=30)
            r.raise_for_status()
            img_path.write_bytes(r.content)
            if prompt:
                txt_path.write_text(prompt, encoding="utf-8")
            downloaded += 1
            if downloaded % 25 == 0:
                print(f"  Downloaded {downloaded} ...")
        except Exception as e:
            print(f"  FAIL {stem}: {e}")

    print()
    print(f"DONE — downloaded {downloaded}, skipped {skipped} dup, no_image {no_image}")
    print(f"  Captions sourced: {captions_from_flux_map} from FLUX prompt map, "
          f"{captions_from_kling} from record's own prompt (Kling-only — less useful)")
    print(f"  Output: {out_dir}")


if __name__ == "__main__":
    main()
