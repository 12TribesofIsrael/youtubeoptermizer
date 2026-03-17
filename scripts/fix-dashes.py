# -*- coding: utf-8 -*-
"""Fix broken em dash characters in all video titles."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

client = YouTubeClient()

print("Scanning all videos for broken dash characters...")
videos = client.list_videos(max_results=300)

# The broken sequence is bytes C3 A2 E2 82 AC 22 which renders as mangled UTF-8
broken_patterns = [
    "\u00e2\u20ac\u201c",  # â€"
    "\u00e2\u20ac\u201d",  # â€"
    "\u00e2\u20ac\u0022",  # â€"
    "\u00c2",              # Â
]

broken = []
for v in videos:
    title = v["snippet"]["title"]
    for pat in broken_patterns:
        if pat in title:
            broken.append(v)
            break

print(f"Found {len(broken)} videos with broken characters")
print("=" * 60)

updated = 0
for v in broken:
    vid = v["id"]
    old_title = v["snippet"]["title"]
    new_title = old_title
    for pat in broken_patterns:
        new_title = new_title.replace(pat, "\u2014")  # proper em dash

    # Clean up double dashes or extra spaces
    new_title = new_title.replace("\u2014\u2014", "\u2014")
    while "  " in new_title:
        new_title = new_title.replace("  ", " ")
    new_title = new_title.strip()

    if new_title == old_title:
        continue

    try:
        client.update_video(vid, title=new_title)
        updated += 1
        print(f"  [{updated}] {repr(old_title)}")
        print(f"       -> {new_title}")
        time.sleep(0.5)
    except Exception as e:
        print(f"  ERROR [{vid}]: {e}")
        if "quotaExceeded" in str(e):
            print("Quota hit.")
            break

print(f"\nFixed: {updated}")
