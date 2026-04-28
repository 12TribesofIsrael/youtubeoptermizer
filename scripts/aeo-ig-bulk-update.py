"""
AEO Instagram caption bulk-update — mirror of scripts/aeo-bulk-update.py for IG.

Appends the canonical AEO constants block (About + canonical URLs + hashtag) to
every IG post caption. Scrubs dissolved-entity refs ("Technology Gurus LLC",
old contact email) on the way through.

Idempotent: skips captions that already have the marker.
Resumable: checkpoints every 10 posts to output/aeo-ig-checkpoint.json.
Paced: 50/post per run by default — pass --limit N to override.

Uses the new IG Business token (graph.instagram.com) approved 2026-04-27, NOT
the old graph.facebook.com surface. Caption updates require comment_enabled=true
or the API rejects with code 100 (per memory feedback_ig_caption_update_comment_enabled).

Run:
    python scripts/aeo-ig-bulk-update.py                # dry-run, first 50
    python scripts/aeo-ig-bulk-update.py --limit 5      # dry-run, sample 5
    python scripts/aeo-ig-bulk-update.py --live         # apply, first 50
    python scripts/aeo-ig-bulk-update.py --live --limit 200
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

# IG captions contain emoji; Windows default cp1252 crashes on print.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
CHECKPOINT = ROOT / "output/aeo-ig-checkpoint.json"

IG_TOKEN = os.getenv("IG_BUSINESS_TOKEN") or os.getenv("META_ACCESS_TOKEN")
IG_BIZ_ID = os.getenv("INSTAGRAM_BUSINESS_ID")
IG_API = "https://graph.instagram.com/v22.0"

MARKER = "— ABOUT AI BIBLE GOSPELS —"

CONSTANTS_BLOCK = """— ABOUT AI BIBLE GOSPELS —
AI Bible Gospels (@AIBIBLEGOSPELS) is a faith-tech brand by Tommy Lee using AI to narrate Scripture from a cultural perspective underrepresented in biblical media. Flagship: Faith Walk Live — the live tracker for Minister Zay's 3,000-mile walk from Philadelphia to California.

Website: aibiblegospels.com
Faith Walk Live: faithwalklive.com
YouTube: youtube.com/@AIBIBLEGOSPELS
Contact: aibiblegospels444@gmail.com

#AIBibleGospels #FaithWalkLive #BibleAI"""

IG_CAPTION_MAX = 2200


def transform_caption(current: str) -> str | None:
    """Return new caption, or None if already has the marker (skip)."""
    if MARKER in current:
        return None
    cleaned = current or ""
    for needle in ("Technology Gurus LLC", "technology gurus llc", "Technology Gurus, LLC"):
        cleaned = cleaned.replace(needle, "")
    cleaned = cleaned.replace("technologygurusllc@gmail.com", "aibiblegospels444@gmail.com")
    cleaned = cleaned.rstrip()

    new_cap = (cleaned + "\n\n" + CONSTANTS_BLOCK) if cleaned else CONSTANTS_BLOCK

    if len(new_cap) > IG_CAPTION_MAX:
        overhead = len(CONSTANTS_BLOCK) + 2
        budget = IG_CAPTION_MAX - overhead
        head = cleaned[:budget].rstrip()
        new_cap = (head + "\n\n" + CONSTANTS_BLOCK) if head else CONSTANTS_BLOCK

    return new_cap


def api_get(url: str) -> dict:
    try:
        r = urllib.request.urlopen(url, timeout=20)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return {"__http_error__": e.code, **json.loads(body)}
        except Exception:
            return {"__http_error__": e.code, "body": body}


def api_post(url: str, data: dict) -> dict:
    encoded = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=encoded, method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=20)
        return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            return {"__http_error__": e.code, **json.loads(body)}
        except Exception:
            return {"__http_error__": e.code, "body": body}


def fetch_all_posts() -> list[dict]:
    posts: list[dict] = []
    url = (
        f"{IG_API}/{IG_BIZ_ID}/media"
        f"?fields=id,caption,timestamp,permalink,media_type"
        f"&limit=100&access_token={IG_TOKEN}"
    )
    while url:
        data = api_get(url)
        if "__http_error__" in data:
            print(f"  ERR fetching media list: {data}")
            break
        posts.extend(data.get("data", []))
        paging = data.get("paging", {})
        url = paging.get("next")
    return posts


def update_caption(media_id: str, new_caption: str) -> dict:
    return api_post(
        f"{IG_API}/{media_id}",
        {
            "caption": new_caption,
            "comment_enabled": "true",
            "access_token": IG_TOKEN,
        },
    )


def load_checkpoint() -> tuple[set, set, set]:
    if CHECKPOINT.exists():
        d = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        return set(d.get("completed", [])), set(d.get("skipped", [])), set(d.get("errored", []))
    return set(), set(), set()


def save_checkpoint(completed: set, skipped: set, errored: set) -> None:
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(
        json.dumps(
            {
                "completed": sorted(completed),
                "skipped": sorted(skipped),
                "errored": sorted(errored),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="apply updates (default: dry-run)")
    ap.add_argument("--limit", type=int, default=50, help="max posts to process this run (default 50)")
    ap.add_argument("--preview", type=int, default=0, help="print N full transformed captions and exit")
    args = ap.parse_args()

    if not IG_TOKEN or not IG_BIZ_ID:
        print("ERR: IG_BUSINESS_TOKEN and INSTAGRAM_BUSINESS_ID must be set in .env")
        sys.exit(1)

    mode = "LIVE" if args.live else "DRY-RUN"
    print(f"AEO IG bulk update — {mode}, limit={args.limit}")
    print("=" * 70)

    print("Fetching all IG media...")
    posts = fetch_all_posts()
    print(f"  found {len(posts)} posts")

    completed, skipped, errored = load_checkpoint()
    todo = []
    for p in posts:
        pid = p["id"]
        if pid in completed or pid in skipped:
            continue
        todo.append(p)

    print(f"  prior completed={len(completed)} skipped={len(skipped)} errored={len(errored)}")
    print(f"  to process this run: min({len(todo)}, {args.limit})")
    print("=" * 70)

    if args.preview:
        shown = 0
        for post in todo:
            original = post.get("caption") or ""
            if not original or len(original) < 5:
                continue
            new_cap = transform_caption(original)
            if new_cap is None:
                continue
            print("\n" + "─" * 70)
            print(f"POST {post['id']}  ({(post.get('timestamp') or '')[:10]})")
            print("─ ORIGINAL " + "─" * 59)
            print(original)
            print("─ NEW " + "─" * 64)
            print(new_cap)
            print(f"─ ({len(new_cap)} chars)")
            shown += 1
            if shown >= args.preview:
                break
        return

    todo = todo[: args.limit]
    if not todo:
        print("Nothing to do. All caught up.")
        return

    rate_limit_hit = False
    for i, post in enumerate(todo, 1):
        media_id = post["id"]
        original = post.get("caption") or ""
        ts = (post.get("timestamp") or "")[:10]
        media_type = post.get("media_type", "")

        if not original or len(original) < 5:
            if args.live:
                skipped.add(media_id)
            print(f"  [{i:>3}/{len(todo)}] SKIP    {media_id}  (no caption)")
            continue

        new_cap = transform_caption(original)
        if new_cap is None:
            if args.live:
                completed.add(media_id)
            print(f"  [{i:>3}/{len(todo)}] ALREADY {media_id}")
            continue

        preview = original.replace("\n", " ")[:55]
        print(f"  [{i:>3}/{len(todo)}] {ts} [{media_type}] {preview}")

        if not args.live:
            print(f"           -> would write {len(new_cap)} chars (dry-run, no checkpoint)")
            continue

        result = update_caption(media_id, new_cap)
        err = result.get("error") or result.get("__http_error__")
        if err:
            err_str = json.dumps(err)
            print(f"           ERR: {err_str[:200]}")
            if any(s in err_str for s in ("rate", "limit", "throttl", "OAuthException")):
                if "OAuthException" in err_str and "expired" in err_str.lower():
                    print("           token appears expired — stop and refresh")
                    rate_limit_hit = True
                    break
                if "rate" in err_str.lower() or "throttl" in err_str.lower():
                    print("           rate-limited — saving checkpoint, stopping")
                    rate_limit_hit = True
                    break
            errored.add(media_id)
        else:
            completed.add(media_id)
            print(f"           OK")

        time.sleep(1.0)

        if i % 10 == 0:
            save_checkpoint(completed, skipped, errored)

    if args.live:
        save_checkpoint(completed, skipped, errored)

    print("=" * 70)
    print("Run summary:")
    print(f"  Completed (cumulative): {len(completed)} / {len(posts)}")
    print(f"  Skipped:                {len(skipped)}")
    print(f"  Errored:                {len(errored)}")
    remaining = len(posts) - len(completed) - len(skipped)
    print(f"  Remaining:              {remaining}")
    if rate_limit_hit:
        print("\n  Stopped early (rate limit / token issue). Re-run after cooldown.")
    if not args.live:
        print("\n  DRY-RUN — no captions were modified. Re-run with --live to apply.")


if __name__ == "__main__":
    main()
