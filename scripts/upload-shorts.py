"""Upload the 6 Faith Walk Live Shorts to YouTube as scheduled drops.

Drips one Short per day at 3 PM ET starting tomorrow. All Shorts are uploaded
as Private with a publishAt timestamp — YouTube auto-flips them to Public on
schedule. Each Short is added to the 'Faith Walk Live — The 3000-Mile Walk'
playlist on upload.

Usage:
    python scripts/upload-shorts.py            # dry-run preview, no upload
    python scripts/upload-shorts.py --live     # actually upload all 6 with schedule
    python scripts/upload-shorts.py --live --start-date 2026-05-09  # override start
"""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.youtube.client import YouTubeClient

OUT_DIR = ROOT / "src" / "shorts" / "out"
PLAYLIST_TITLE = "Faith Walk Live — The 3000-Mile Walk"

# Mirrors src/shorts/src/shorts.ts metadata (kept in sync manually).
SHORTS_META = [
    {
        "file": "01-the-why.mp4",  # comp id: s1-why
        "title": "He's walking 3000 miles. Here's why. #FaithWalkLive #Shorts",
        "description": "Minister Humble Zay explains why he's walking 3,000 miles from Philadelphia to California — to build a school for at-risk Philly kids.\n\nFull documentary on the channel.\n\n🥾 Track the walk live: https://faithwalklive.com\n💰 Donate to the school: https://gofund.me/19cf823bc\n🎥 Live on Twitch: https://www.twitch.tv/hmblzayy\n\n#AIBibleGospels #FaithWalkLive #HumbleZay #Shorts",
    },
    {
        "file": "s2-hit.mp4",
        "title": "Hit by a car on Day 19. Walking again Day 20. #FaithWalkLive #Shorts",
        "description": "Minister Zay was struck by a vehicle on US-40 in Indiana during his 3,000-mile walk. Five days later, he was back on the road.\n\nFull documentary on the channel.\n\n🥾 Track the walk live: https://faithwalklive.com\n💰 Donate to the school: https://gofund.me/19cf823bc\n🎥 Live on Twitch: https://www.twitch.tv/hmblzayy\n\n#AIBibleGospels #FaithWalkLive #HumbleZay #Shorts",
    },
    {
        "file": "s3-auntie.mp4",
        "title": "Strangers showing up for him 3000 miles in #FaithWalkLive #Shorts",
        "description": "Indianapolis aunties pull up to support Minister Zay during his 3,000-mile walk. The community is showing up at every stop.\n\nFull documentary on the channel.\n\n🥾 Track the walk live: https://faithwalklive.com\n💰 Donate to the school: https://gofund.me/19cf823bc\n🎥 Live on Twitch: https://www.twitch.tv/hmblzayy\n\n#AIBibleGospels #FaithWalkLive #HumbleZay #Shorts",
    },
    {
        "file": "s4-hokas.mp4",
        "title": "Community gifted him new shoes when his blew out #FaithWalkLive #Shorts",
        "description": "Halfway through 3,000 miles on foot, Zay's shoes blew out. Within hours, the community gifted him new ones.\n\nFull documentary on the channel.\n\n🥾 Track the walk live: https://faithwalklive.com\n💰 Donate to the school: https://gofund.me/19cf823bc\n🎥 Live on Twitch: https://www.twitch.tv/hmblzayy\n\n#AIBibleGospels #FaithWalkLive #HumbleZay #Shorts",
    },
    {
        "file": "s5-milestone.mp4",
        "title": "Day 44 of 3000 miles — Indianapolis #FaithWalkLive #Shorts",
        "description": "Six weeks into a 3,000-mile walk from Philadelphia to California. Real-time tracker at faithwalklive.com.\n\nFull documentary on the channel.\n\n🥾 Track the walk live: https://faithwalklive.com\n💰 Donate to the school: https://gofund.me/19cf823bc\n🎥 Live on Twitch: https://www.twitch.tv/hmblzayy\n\n#AIBibleGospels #FaithWalkLive #HumbleZay #Shorts",
    },
    {
        "file": "s6-test.mp4",
        "title": "What it actually takes to walk 3000 miles #FaithWalkLive #Shorts",
        "description": "Rain. No food. Potholes. Still walking. The brutal reality of 3,000 miles on foot.\n\nFull documentary on the channel.\n\n🥾 Track the walk live: https://faithwalklive.com\n💰 Donate to the school: https://gofund.me/19cf823bc\n🎥 Live on Twitch: https://www.twitch.tv/hmblzayy\n\n#AIBibleGospels #FaithWalkLive #HumbleZay #Shorts",
    },
]

TAGS = [
    "Humble Zay", "Faith Walk Live", "faithwalklive.com", "3000 mile walk",
    "Philly walk", "AI Bible Gospels", "walking documentary", "Hebrew Israelite",
    "Shorts", "FaithWalkLive",
]

CATEGORY_ID = "27"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="Actually upload (default: dry-run preview)")
    ap.add_argument("--start-date", default=None, help="ISO date YYYY-MM-DD; default = tomorrow")
    args = ap.parse_args()

    # Schedule: 3 PM ET = 19:00 UTC (assuming EDT/UTC-4 around May 2026; YT
    # accepts UTC and applies the channel-set timezone for display).
    if args.start_date:
        start = datetime.fromisoformat(args.start_date).replace(tzinfo=timezone.utc)
    else:
        start = datetime.now(timezone.utc) + timedelta(days=1)
    start = start.replace(hour=19, minute=0, second=0, microsecond=0)

    print(f"Mode:        {'LIVE' if args.live else 'DRY-RUN preview'}")
    print(f"Start drop:  {start.isoformat()} (3 PM ET / 19:00 UTC)")
    print()

    yt = YouTubeClient()
    youtube = yt.youtube

    # Find existing playlist
    playlist_id = None
    if args.live:
        playlists = yt.list_playlists()
        target = next((p for p in playlists if p["snippet"]["title"] == PLAYLIST_TITLE), None)
        if target:
            playlist_id = target["id"]
            print(f"Playlist: {playlist_id}\n")
        else:
            print(f"WARN: playlist '{PLAYLIST_TITLE}' not found. Shorts won't be added to it.\n")

    drops = []
    for i, meta in enumerate(SHORTS_META):
        publish_at = start + timedelta(days=i)
        path = OUT_DIR / meta["file"]
        if not path.exists():
            print(f"  [{i+1}/6] MISSING: {path.name} — render it first. Skipping.")
            continue
        size_mb = path.stat().st_size / 1e6
        print(f"  [{i+1}/6] {publish_at.strftime('%a %b %d %I:%M %p UTC'):28s} {meta['file']} ({size_mb:.1f} MB)")
        print(f"           {meta['title']}")

        if not args.live:
            continue

        body = {
            "snippet": {
                "title": meta["title"],
                "description": meta["description"],
                "tags": TAGS,
                "categoryId": CATEGORY_ID,
            },
            "status": {
                "privacyStatus": "private",  # private + publishAt = scheduled drop
                "publishAt": publish_at.isoformat(),
                "selfDeclaredMadeForKids": False,
                "madeForKids": False,
            },
        }
        media = MediaFileUpload(str(path), chunksize=4 * 1024 * 1024, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"           upload {int(status.progress() * 100)}%")
        video_id = response["id"]
        print(f"           Done. video_id = {video_id}")
        drops.append({"video_id": video_id, "title": meta["title"], "publishAt": publish_at.isoformat(), "file": meta["file"]})

        # Add to playlist
        if playlist_id:
            yt.add_to_playlist(playlist_id, video_id)
            print(f"           Added to playlist.")

    if args.live and drops:
        log = ROOT / "output" / "shorts-drop-schedule.json"
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(json.dumps(drops, indent=2), encoding="utf-8")
        print(f"\nDrop schedule saved to {log.relative_to(ROOT)}")
        print("\nAll 6 Shorts uploaded as Private with publishAt scheduled.")
        print("YouTube will auto-flip each to Public at its scheduled time.")
    elif not args.live:
        print(f"\n{len(SHORTS_META)} Shorts ready to upload. Re-run with --live to ship.")


if __name__ == "__main__":
    main()
