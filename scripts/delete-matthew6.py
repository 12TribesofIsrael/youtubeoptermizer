"""Delete Matthew 6 flood videos, keeping the top performer."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

client = YouTubeClient()

# Keep: TxO-08eVvVw (740 views) — "Book of Matthew 6 #godsays #motivation..."
# Delete the rest:
to_delete = [
    ("MbDzov2sT6c", 383),
    ("EFGQB8h8hAo", 324),
    ("4U2jkTkYYpA", 250),
    ("jAwoWZbiQeE", 123),
    ("3ePJ8t-MOXU", 14),
]

print(f"Deleting {len(to_delete)} Matthew 6 flood videos (keeping TxO-08eVvVw)")
print("=" * 60)

deleted = 0
for vid, views in to_delete:
    try:
        video = client.get_video(vid)
        if not video:
            print(f"  SKIP [{vid}] — not found")
            continue
        title = video["snippet"]["title"]
        client.delete_video(vid)
        deleted += 1
        print(f"  DELETED [{vid}] {title} ({views} views)")
        time.sleep(0.5)
    except Exception as e:
        print(f"  ERROR [{vid}]: {e}")

print(f"\nDeleted: {deleted}")
