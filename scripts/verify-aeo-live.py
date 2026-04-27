"""Live verification — fetch random video descriptions from YouTube and check
whether the AEO constants block is actually present right now."""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

MARKER = "— ABOUT AI BIBLE GOSPELS —"

# Sample IDs pulled from the completed checkpoint (mix of recent + older)
SAMPLE_IDS = [
    "0JMTqU5DhZQ", "KGVZHGopiQ0", "PCxBqyvr8NA", "TBNEIWRpnzI", "WBTvL8yDu70",
    "gAgEL09nLRU", "hJDgZIu3gas", "izvPfu1UjkM", "rKLtGlKw4ak", "xb8pPrCgFo4",
]


def main():
    yt = YouTubeClient()
    resp = yt.youtube.videos().list(
        part="snippet",
        id=",".join(SAMPLE_IDS),
        maxResults=50,
    ).execute()

    items = resp.get("items", [])
    print(f"Fetched {len(items)} of {len(SAMPLE_IDS)} sample IDs\n")

    have_marker = 0
    missing = []
    for it in items:
        vid = it["id"]
        title = it["snippet"]["title"][:55]
        desc = it["snippet"]["description"]
        has = MARKER in desc
        if has:
            have_marker += 1
        else:
            missing.append(vid)
        flag = "OK " if has else "MISS"
        print(f"{flag}  {vid}  {title}")

    print(f"\nMarker present: {have_marker}/{len(items)}")
    if missing:
        print(f"Missing: {missing}")


if __name__ == "__main__":
    main()
