"""Remove @AIBIBLEGOSPELS from all video titles."""

import sys
import re
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

client = YouTubeClient()

# Load audit data
audit_file = Path(__file__).resolve().parent.parent / "analytics" / "audit-results.json"
audit = json.loads(audit_file.read_text())

handle_videos = audit["handle_in_title"]
print(f"Found {len(handle_videos)} videos with @AIBIBLEGOSPELS in title")
print("=" * 60)

updated = 0
errors = []

for v in handle_videos:
    vid = v["id"]
    old_title = v["title"]

    # Remove @AIBIBLEGOSPELS and clean up whitespace
    new_title = old_title.replace("@AIBIBLEGOSPELS", "").replace("@aibiblegospels", "")
    # Clean double spaces and trailing/leading whitespace
    new_title = re.sub(r"\s{2,}", " ", new_title).strip()
    # Remove trailing punctuation artifacts like trailing comma, dash, pipe
    new_title = re.sub(r"[\s,\-|]+$", "", new_title).strip()

    if new_title == old_title:
        continue

    try:
        client.update_video(vid, title=new_title)
        updated += 1
        print(f"  [{updated}] {old_title}")
        print(f"       → {new_title}")
        # Small delay to stay within quota
        time.sleep(0.5)
    except Exception as e:
        errors.append({"id": vid, "title": old_title, "error": str(e)})
        print(f"  ERROR [{vid}] {old_title}: {e}")

print(f"\n{'=' * 60}")
print(f"Updated: {updated} titles")
print(f"Errors:  {len(errors)}")
if errors:
    print("\nFailed videos:")
    for e in errors:
        print(f"  [{e['id']}] {e['error']}")
