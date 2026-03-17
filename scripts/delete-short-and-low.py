"""Delete very short videos (<15s) and low performers (<30 views)."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

client = YouTubeClient()

to_delete = [
    # Very short (<15s)
    ("tm7WlZ7A85w", "8s, 170 views"),
    ("VpDeAEbK2cA", "11s, 51 views"),
    ("BoMLiQDwwo8", "13s, 982 views"),
    ("8o0oDlRCAKc", "4s, 1593 views"),
    # Low performers (<30 views)
    ("FL2X41cjCVs", "11 views"),
    ("fwFx-3qy1S8", "13 views"),
    ("vfrGj7jOGbk", "15 views"),
    ("e3XFPdsTTvs", "16 views"),
    ("MoHNAkcvuQ4", "16 views"),
    ("U6Si4hbf1lI", "18 views"),
    ("AXYOKOD6GFs", "22 views"),
    ("ZTRImPlvwgE", "24 views"),
    ("7Uw_TQ1yscU", "24 views"),
    ("KVWUcoV2nOI", "25 views"),
    ("mvQ4BQILSd8", "26 views"),
]

print(f"Deleting {len(to_delete)} videos (short + low performers)")
print("=" * 60)

deleted = 0
for vid, reason in to_delete:
    try:
        video = client.get_video(vid)
        if not video:
            print(f"  SKIP [{vid}] — not found")
            continue
        title = video["snippet"]["title"]
        client.delete_video(vid)
        deleted += 1
        print(f"  DELETED [{vid}] {title} ({reason})")
        time.sleep(0.5)
    except Exception as e:
        print(f"  ERROR [{vid}]: {e}")

print(f"\nDeleted: {deleted}")
