"""
AEO Instagram comment-pin rollout — pivot from caption edits.

The IG Graph API silently no-ops `caption` edits on existing posts (200 OK,
caption unchanged — see .claude/memory/feedback_ig_caption_update_comment_enabled.md).
This script instead POSTs the canonical AEO constants block as a comment, then
pins it. Comments are indexed by answer engines and the
`instagram_business_manage_comments` scope was approved 2026-04-27.

Idempotent: skips posts whose comment list already contains the marker.
Resumable: checkpoints every 10 posts to output/aeo-ig-comment-checkpoint.json.
Default: dry-run, latest 1 post (canary-first posture).

Run:
    python scripts/aeo-ig-pin-comment.py                          # dry-run, latest 1
    python scripts/aeo-ig-pin-comment.py --media-id 17xxx         # dry-run, specific
    python scripts/aeo-ig-pin-comment.py --live --media-id 17xxx  # CANARY
    python scripts/aeo-ig-pin-comment.py --live --limit 5         # later
    python scripts/aeo-ig-pin-comment.py --live --limit 50        # full pace
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
CHECKPOINT = ROOT / "output/aeo-ig-comment-checkpoint.json"

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


def fetch_one_post(media_id: str) -> dict | None:
    url = (
        f"{IG_API}/{media_id}"
        f"?fields=id,caption,timestamp,permalink,media_type"
        f"&access_token={IG_TOKEN}"
    )
    data = api_get(url)
    if "__http_error__" in data:
        print(f"  ERR fetching media {media_id}: {data}")
        return None
    return data


def fetch_comments(media_id: str) -> list[dict]:
    """Return all comments on a media, paginated."""
    comments: list[dict] = []
    url = (
        f"{IG_API}/{media_id}/comments"
        f"?fields=id,text&limit=50&access_token={IG_TOKEN}"
    )
    while url:
        data = api_get(url)
        if "__http_error__" in data:
            print(f"           ERR fetching comments: {json.dumps(data)[:200]}")
            return comments
        comments.extend(data.get("data", []))
        paging = data.get("paging", {})
        url = paging.get("next")
    return comments


def find_aeo_comment(comments: list[dict]) -> dict | None:
    for c in comments:
        if MARKER in (c.get("text") or ""):
            return c
    return None


def post_comment(media_id: str, message: str) -> dict:
    return api_post(
        f"{IG_API}/{media_id}/comments",
        {"message": message, "access_token": IG_TOKEN},
    )


def pin_comment(comment_id: str) -> dict:
    # IG comment-mutation endpoint requires `hide` alongside `is_pinned`.
    return api_post(
        f"{IG_API}/{comment_id}",
        {"is_pinned": "true", "hide": "false", "access_token": IG_TOKEN},
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
    do_pin: bool,
    completed: set,
    errored: set,
    idx: int,
    total: int,
) -> str:
    """Returns one of: 'completed', 'errored', 'already'."""
    media_id = post["id"]
    ts = (post.get("timestamp") or "")[:10]
    media_type = post.get("media_type", "")
    permalink = post.get("permalink", "")

    print(f"  [{idx:>3}/{total}] {ts} [{media_type}] {media_id}")
    print(f"           {permalink}")

    existing = fetch_comments(media_id)
    aeo = find_aeo_comment(existing)
    if aeo:
        print(f"           ALREADY  comment_id={aeo['id']}")
        if live:
            completed.add(media_id)
        return "already"

    if not live:
        print(f"           DRY-RUN  would POST + pin AEO comment ({len(CONSTANTS_BLOCK)} chars)")
        return "completed"

    post_result = post_comment(media_id, CONSTANTS_BLOCK)
    err = post_result.get("error") or post_result.get("__http_error__")
    if err:
        print(f"           POST ERR: {json.dumps(err)[:200]}")
        errored.add(media_id)
        return "errored"

    comment_id = post_result.get("id")
    if not comment_id:
        print(f"           POST returned no id: {json.dumps(post_result)[:200]}")
        errored.add(media_id)
        return "errored"
    print(f"           POSTED   comment_id={comment_id}")

    if do_pin:
        pin_result = pin_comment(comment_id)
        pin_err = pin_result.get("error") or pin_result.get("__http_error__")
        if pin_err:
            print(f"           PIN ERR: {json.dumps(pin_err)[:200]}")
        else:
            print(f"           PINNED")
    else:
        print(f"           PIN SKIPPED (--no-pin)")

    refetched = fetch_comments(media_id)
    if find_aeo_comment(refetched):
        print(f"           VERIFIED")
        completed.add(media_id)
        return "completed"
    else:
        print(f"           MISSING — POST returned 200 but comment not in re-fetch")
        errored.add(media_id)
        return "errored"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="apply (default: dry-run)")
    ap.add_argument("--limit", type=int, default=1, help="max posts this run (default 1, canary-first)")
    ap.add_argument("--media-id", type=str, default=None, help="target a specific post id")
    ap.add_argument("--no-pin", action="store_true", help="skip the pin step (POST only)")
    ap.add_argument("--retry-pin", type=str, default=None, help="retry pin on an existing comment id, then exit")
    ap.add_argument("--delete-comment-id", type=str, default=None, help="DELETE an existing comment id, then exit (ops recovery)")
    args = ap.parse_args()

    if args.retry_pin:
        if not IG_TOKEN:
            print("ERR: IG_BUSINESS_TOKEN not set")
            sys.exit(1)
        print(f"Retry pin on comment {args.retry_pin}...")
        result = pin_comment(args.retry_pin)
        err = result.get("error") or result.get("__http_error__")
        if err:
            print(f"  PIN ERR: {json.dumps(err)[:300]}")
            sys.exit(2)
        print(f"  PINNED  {json.dumps(result)[:200]}")
        return

    if args.delete_comment_id:
        if not IG_TOKEN:
            print("ERR: IG_BUSINESS_TOKEN not set")
            sys.exit(1)
        url = f"{IG_API}/{args.delete_comment_id}?access_token={IG_TOKEN}"
        req = urllib.request.Request(url, method="DELETE")
        try:
            r = urllib.request.urlopen(req, timeout=20)
            body = r.read().decode("utf-8", errors="replace")
            print(f"Deleted comment {args.delete_comment_id}: {body}")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"DELETE ERR: {e.code} {body[:300]}")
            sys.exit(2)
        return

    if not IG_TOKEN or not IG_BIZ_ID:
        print("ERR: IG_BUSINESS_TOKEN and INSTAGRAM_BUSINESS_ID must be set in .env")
        sys.exit(1)

    mode = "LIVE" if args.live else "DRY-RUN"
    print(f"AEO IG comment-pin — {mode}")
    if args.media_id:
        print(f"  target: media_id={args.media_id}")
    else:
        print(f"  limit:  {args.limit} (latest)")
    print(f"  pin:    {'NO' if args.no_pin else 'YES'}")
    print("=" * 70)

    completed, skipped, errored = load_checkpoint()

    if args.media_id:
        post = fetch_one_post(args.media_id)
        if not post:
            sys.exit(2)
        todo = [post]
    else:
        print("Fetching IG media...")
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
            do_pin=not args.no_pin,
            completed=completed,
            errored=errored,
            idx=i,
            total=len(todo),
        )

        if args.live:
            time.sleep(1.0)
            if i % 10 == 0:
                save_checkpoint(completed, skipped, errored)

        if result == "errored":
            # Save and stop on rate-limit / abuse-flag / token issues so a re-run resumes cleanly.
            if args.live:
                save_checkpoint(completed, skipped, errored)
            print("           saving checkpoint, stopping run on first error")
            break

    if args.live:
        save_checkpoint(completed, skipped, errored)

    print("=" * 70)
    print("Run summary:")
    print(f"  Completed (cumulative): {len(completed)}")
    print(f"  Skipped:                {len(skipped)}")
    print(f"  Errored:                {len(errored)}")
    if not args.live:
        print("\n  DRY-RUN — no comments were posted. Re-run with --live to apply.")


if __name__ == "__main__":
    main()
