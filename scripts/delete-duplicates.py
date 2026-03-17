"""Delete duplicate part-numbered videos, keeping the higher-view version."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

client = YouTubeClient()

# Duplicate parts: delete the lower-view version
# Format: (video_id, title, views) — these are the ones to DELETE
to_delete = [
    ("_VyT3Wja8rI", "Part 11 (duplicate)", 9728),
    ("Iu9j9lbO1L0", "Part 10 (duplicate)", 2250),
    ("7lEXIjb1w8c", "Part 8 (duplicate)", 1178),
    ("OP8DH3QeOlM", "Part 15 (duplicate)", 5095),
    ("CoqyWeGFwik", "Part 22 (duplicate)", 3651),
    ("_zhWsE36dss", "Part 23 (duplicate)", 986),
    ("Mgkob7zPCXg", "Part 66 (duplicate)", 1545),
    ("MAkhk-cIuvE", "Part 75 (duplicate)", 727),
    # Part 52 has 3 copies — keep 8o0oDlRCAKc (1593 views), delete other two
    ("QTsCcJxRhsc", "Part 52 (duplicate #2)", 145),
    ("sbv8oJWTgHk", "Part 52 (duplicate #3)", 118),
]

print(f"Deleting {len(to_delete)} duplicate part videos")
print("=" * 60)

deleted = 0
errors = []

for vid, label, views in to_delete:
    try:
        # Verify the video exists before deleting
        video = client.get_video(vid)
        if not video:
            print(f"  SKIP [{vid}] {label} — not found (already deleted?)")
            continue

        actual_title = video["snippet"]["title"]
        client.delete_video(vid)
        deleted += 1
        print(f"  DELETED [{vid}] {actual_title} ({views} views)")
        time.sleep(0.5)
    except Exception as e:
        errors.append({"id": vid, "label": label, "error": str(e)})
        print(f"  ERROR [{vid}] {label}: {e}")

print(f"\n{'=' * 60}")
print(f"Deleted: {deleted}")
print(f"Errors:  {len(errors)}")
