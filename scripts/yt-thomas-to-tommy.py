"""
YT description scrub: 'Thomas Lee' → 'Tommy Lee' across all live videos.

Phase A AEO rollout (committed fc03923) pushed the AEO constants block to 213
live videos with the user's legal name in it. This script walks every live
video and rewrites the description in place.

Idempotent: skips videos whose description doesn't contain 'Thomas Lee'.
Resumable: checkpoints every 10 videos to output/yt-thomas-to-tommy-checkpoint.json.
Quota-aware: stops cleanly on quotaExceeded.
Default: dry-run, latest 1 video (canary-first).

YT Data v3 quota: 1 unit (videos.list) + 50 units (videos.update) = 51/video.
Daily limit 10,000 → ~196 videos/day before hitting quota.

Run:
    python scripts/yt-thomas-to-tommy.py                      # dry-run, latest 1
    python scripts/yt-thomas-to-tommy.py --video-id <id>      # dry-run, specific
    python scripts/yt-thomas-to-tommy.py --live --video-id <id>  # CANARY
    python scripts/yt-thomas-to-tommy.py --live --limit 50    # batch
    python scripts/yt-thomas-to-tommy.py --live --limit 250   # full pace, will hit quota
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

ROOT = Path(__file__).resolve().parent.parent
CHECKPOINT = ROOT / "output/yt-thomas-to-tommy-checkpoint.json"

NEEDLE = "Thomas Lee"
REPLACEMENT = "Tommy Lee"


def fetch_all_uploaded_video_ids(client) -> list[str]:
    """Walk the channel's uploads playlist for the current set of live video IDs.
    De-dupes — the playlist can return the same video_id more than once across pages."""
    ch = client.youtube.channels().list(part="contentDetails", mine=True).execute()
    uploads_pl = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    seen: set[str] = set()
    ids: list[str] = []
    req = client.youtube.playlistItems().list(
        part="contentDetails", playlistId=uploads_pl, maxResults=50
    )
    while req:
        r = req.execute()
        for it in r.get("items", []):
            vid = it["contentDetails"]["videoId"]
            if vid not in seen:
                seen.add(vid)
                ids.append(vid)
        req = client.youtube.playlistItems().list_next(req, r)
    return ids


def load_checkpoint():
    if CHECKPOINT.exists():
        d = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        return set(d.get("completed", [])), set(d.get("skipped", [])), set(d.get("errored", []))
    return set(), set(), set()


def save_checkpoint(completed, skipped, errored):
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="apply (default: dry-run)")
    ap.add_argument("--limit", type=int, default=1, help="max videos this run (default 1, canary-first)")
    ap.add_argument("--video-id", type=str, default=None, help="target a specific video id")
    args = ap.parse_args()

    client = YouTubeClient()

    if args.video_id:
        video_ids = [args.video_id]
    else:
        print("Fetching uploads playlist (live videos only)...")
        video_ids = fetch_all_uploaded_video_ids(client)
        print(f"  found {len(video_ids)} live videos")

    completed, skipped, errored = load_checkpoint()
    todo = [v for v in video_ids if v not in completed and v not in skipped]
    if not args.video_id:
        todo = todo[: args.limit]

    mode = "LIVE" if args.live else "DRY-RUN"
    print(f"YT scrub 'Thomas Lee' -> 'Tommy Lee' — {mode}")
    print(f"  prior completed={len(completed)} skipped={len(skipped)} errored={len(errored)}")
    print(f"  to process this run: {len(todo)}")
    print("=" * 70)

    if not todo:
        print("Nothing to do.")
        return

    quota_hit = False
    for i, vid in enumerate(todo, 1):
        try:
            video = client.get_video(vid)
            if not video:
                print(f"  [{i:>3}/{len(todo)}] {vid}  SKIP (not found)")
                if args.live:
                    skipped.add(vid)
                continue

            current_desc = video["snippet"].get("description", "") or ""
            title = video["snippet"]["title"][:55]

            if NEEDLE not in current_desc:
                print(f"  [{i:>3}/{len(todo)}] {vid}  CLEAN (no '{NEEDLE}')  {title}")
                if args.live:
                    completed.add(vid)
                continue

            count = current_desc.count(NEEDLE)
            new_desc = current_desc.replace(NEEDLE, REPLACEMENT)
            print(f"  [{i:>3}/{len(todo)}] {vid}  {title}")
            print(f"           {count}x '{NEEDLE}' found")

            if not args.live:
                print(f"           DRY-RUN  would replace with '{REPLACEMENT}'")
                continue

            client.update_video(vid, description=new_desc)
            completed.add(vid)
            print(f"           OK")
            time.sleep(0.4)

        except Exception as e:
            err_str = str(e)
            if "quotaExceeded" in err_str or "rateLimitExceeded" in err_str or "userRateLimitExceeded" in err_str:
                print(f"  [{i:>3}/{len(todo)}] QUOTA HIT at {vid} — saving checkpoint and exiting.")
                quota_hit = True
                break
            errored.add(vid)
            print(f"  [{i:>3}/{len(todo)}] ERR     {vid}: {e}")

        if i % 10 == 0 and args.live:
            save_checkpoint(completed, skipped, errored)

    if args.live:
        save_checkpoint(completed, skipped, errored)

    print("=" * 70)
    print("Run summary:")
    print(f"  Completed (cumulative): {len(completed)}")
    print(f"  Skipped (clean/missing): {len(skipped)}")
    print(f"  Errored:                {len(errored)}")
    if quota_hit:
        print("\n  Quota exhausted. Re-run tomorrow (PT midnight reset) to resume.")
    if not args.live:
        print("\n  DRY-RUN — no descriptions were modified. Re-run with --live to apply.")


if __name__ == "__main__":
    main()
