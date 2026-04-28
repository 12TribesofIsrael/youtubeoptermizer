"""
AEO Facebook Page caption bulk-update — script 1B.

Appends the canonical AEO constants block to every FB Page post's `message`.
Unlike IG (which silently no-ops caption edits), FB Graph genuinely persists
`message` rewrites on already-published posts.

Idempotent: skips posts whose message already contains the marker.
Resumable: checkpoints every 10 posts to output/aeo-fb-checkpoint.json.
Default: dry-run, latest 1 post (canary-first posture).

Run:
    python scripts/aeo-fb-bulk-update.py                       # dry-run, latest 1
    python scripts/aeo-fb-bulk-update.py --post-id <id>        # dry-run, specific
    python scripts/aeo-fb-bulk-update.py --live --post-id <id> # CANARY
    python scripts/aeo-fb-bulk-update.py --live --limit 5      # later
    python scripts/aeo-fb-bulk-update.py --live --limit 50     # full pace
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

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
CHECKPOINT = ROOT / "output/aeo-fb-checkpoint.json"

FB_TOKEN = os.getenv("META_PAGE_TOKEN") or os.getenv("META_ACCESS_TOKEN")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FB_API = "https://graph.facebook.com/v25.0"

MARKER = "— ABOUT AI BIBLE GOSPELS —"

CONSTANTS_BLOCK = """— ABOUT AI BIBLE GOSPELS —
AI Bible Gospels (@AIBIBLEGOSPELS) is a faith-tech brand by Tommy Lee using AI to narrate Scripture from a cultural perspective underrepresented in biblical media. Flagship: Faith Walk Live — the live tracker for Minister Zay's 3,000-mile walk from Philadelphia to California.

Website: aibiblegospels.com
Faith Walk Live: faithwalklive.com
YouTube: youtube.com/@AIBIBLEGOSPELS
Contact: aibiblegospels444@gmail.com

#AIBibleGospels #FaithWalkLive #BibleAI"""


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
        f"{FB_API}/{PAGE_ID}/posts"
        f"?fields=id,message,story,created_time,permalink_url"
        f"&limit=100&access_token={FB_TOKEN}"
    )
    while url:
        data = api_get(url)
        if "__http_error__" in data:
            print(f"  ERR fetching FB posts: {data}")
            break
        posts.extend(data.get("data", []))
        paging = data.get("paging", {})
        url = paging.get("next")
    return posts


def fetch_one_post(post_id: str) -> dict | None:
    url = (
        f"{FB_API}/{post_id}"
        f"?fields=id,message,story,created_time,permalink_url"
        f"&access_token={FB_TOKEN}"
    )
    data = api_get(url)
    if "__http_error__" in data:
        print(f"  ERR fetching post {post_id}: {data}")
        return None
    return data


def transform_message(current: str) -> str | None:
    """Return new message, or None if already has the marker (skip)."""
    if MARKER in current:
        return None
    cleaned = current or ""
    for needle in ("Technology Gurus LLC", "technology gurus llc", "Technology Gurus, LLC"):
        cleaned = cleaned.replace(needle, "")
    cleaned = cleaned.replace("technologygurusllc@gmail.com", "aibiblegospels444@gmail.com")
    cleaned = cleaned.rstrip()
    return (cleaned + "\n\n" + CONSTANTS_BLOCK) if cleaned else CONSTANTS_BLOCK


def update_message(post_id: str, new_message: str) -> dict:
    return api_post(
        f"{FB_API}/{post_id}",
        {"message": new_message, "access_token": FB_TOKEN},
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


def process_post(
    post: dict,
    *,
    live: bool,
    completed: set,
    skipped: set,
    errored: set,
    idx: int,
    total: int,
) -> str:
    post_id = post["id"]
    original = post.get("message") or ""
    created = (post.get("created_time") or "")[:10]
    permalink = post.get("permalink_url") or "(no permalink)"

    print(f"  [{idx:>3}/{total}] {created} {post_id}")
    print(f"           {permalink}")

    if not original or len(original) < 5:
        print(f"           SKIP    (no message — likely story-only post)")
        if live:
            skipped.add(post_id)
        return "skipped"

    new_msg = transform_message(original)
    if new_msg is None:
        print(f"           ALREADY (marker present)")
        if live:
            completed.add(post_id)
        return "already"

    preview = original.replace("\n", " ")[:55]
    print(f"           current: {preview}")

    if not live:
        print(f"           DRY-RUN  would write {len(new_msg)} chars")
        return "completed"

    result = update_message(post_id, new_msg)
    err = result.get("error") or result.get("__http_error__")
    if err:
        print(f"           ERR: {json.dumps(err)[:300]}")
        errored.add(post_id)
        return "errored"

    refetched = fetch_one_post(post_id)
    if refetched and MARKER in (refetched.get("message") or ""):
        print(f"           VERIFIED")
        completed.add(post_id)
        return "completed"
    else:
        print(f"           MISSING — write returned 200 but marker not in re-fetch")
        errored.add(post_id)
        return "errored"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="apply (default: dry-run)")
    ap.add_argument("--limit", type=int, default=1, help="max posts this run (default 1, canary-first)")
    ap.add_argument("--post-id", type=str, default=None, help="target a specific post id")
    args = ap.parse_args()

    if not FB_TOKEN or not PAGE_ID:
        print("ERR: META_ACCESS_TOKEN and FACEBOOK_PAGE_ID must be set in .env")
        sys.exit(1)

    mode = "LIVE" if args.live else "DRY-RUN"
    print(f"AEO FB bulk-update — {mode}")
    if args.post_id:
        print(f"  target: post_id={args.post_id}")
    else:
        print(f"  limit:  {args.limit} (latest)")
    print("=" * 70)

    completed, skipped, errored = load_checkpoint()

    if args.post_id:
        post = fetch_one_post(args.post_id)
        if not post:
            sys.exit(2)
        todo = [post]
    else:
        print("Fetching FB posts...")
        all_posts = fetch_all_posts()
        print(f"  found {len(all_posts)} posts")
        todo = [p for p in all_posts if p["id"] not in completed and p["id"] not in skipped]
        todo = todo[: args.limit]

    if not todo:
        print("Nothing to do.")
        return

    print(f"  prior completed={len(completed)} skipped={len(skipped)} errored={len(errored)}")
    print("=" * 70)

    for i, post in enumerate(todo, 1):
        result = process_post(
            post,
            live=args.live,
            completed=completed,
            skipped=skipped,
            errored=errored,
            idx=i,
            total=len(todo),
        )

        if args.live:
            time.sleep(0.5)
            if i % 10 == 0:
                save_checkpoint(completed, skipped, errored)

    if args.live:
        save_checkpoint(completed, skipped, errored)

    print("=" * 70)
    print("Run summary:")
    print(f"  Completed (cumulative): {len(completed)}")
    print(f"  Skipped:                {len(skipped)}")
    print(f"  Errored:                {len(errored)}")
    if not args.live:
        print("\n  DRY-RUN — no posts were modified. Re-run with --live to apply.")


if __name__ == "__main__":
    main()
