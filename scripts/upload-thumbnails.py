# -*- coding: utf-8 -*-
"""Batch upload thumbnails from the thumbnails/ folder."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

client = YouTubeClient()

thumb_dir = Path(__file__).resolve().parent.parent / "thumbnails"
thumbnails = list(thumb_dir.glob("*.png")) + list(thumb_dir.glob("*.jpg"))

print(f"Found {len(thumbnails)} thumbnails to upload")
print("=" * 60)

uploaded = 0
errors = []

for img in thumbnails:
    vid = img.stem  # filename without extension = video ID
    try:
        client.set_thumbnail(vid, str(img))
        uploaded += 1
        print(f"  [{uploaded}] {vid} — uploaded")
        time.sleep(0.5)
    except Exception as e:
        errors.append({"id": vid, "error": str(e)})
        print(f"  ERROR [{vid}]: {e}")
        if "quotaExceeded" in str(e):
            print("Quota hit.")
            break

print(f"\n{'=' * 60}")
print(f"Uploaded: {uploaded}")
print(f"Errors:  {len(errors)}")
