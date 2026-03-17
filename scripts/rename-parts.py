"""Push approved title renames and move Part numbers to descriptions."""

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

client = YouTubeClient()

proposals_file = Path(__file__).resolve().parent.parent / "analytics" / "proposed-titles.json"
proposals = json.loads(proposals_file.read_text())

print(f"Renaming {len(proposals)} videos...")
print("=" * 60)

updated = 0
errors = []

for p in proposals:
    vid = p["id"]
    new_title = p["new_title"]
    part_num = p["part_num"]

    try:
        video = client.get_video(vid)
        if not video:
            print(f"  SKIP [{vid}] — not found")
            continue

        old_desc = video["snippet"].get("description", "")

        # Prepend Part number to description if not already there
        part_line = f"Part {part_num} of The Prophecy Revealed series"
        if f"Part {part_num}" not in old_desc:
            new_desc = f"{part_line}\n\n{old_desc}"
        else:
            new_desc = old_desc

        client.update_video(vid, title=new_title, description=new_desc)
        updated += 1
        print(f"  [{updated}] Part {part_num} → {new_title}")
        time.sleep(0.5)
    except Exception as e:
        errors.append({"id": vid, "part_num": part_num, "title": new_title, "error": str(e)})
        print(f"  ERROR [{vid}] Part {part_num}: {e}")
        if "quotaExceeded" in str(e):
            print(f"\nQuota hit after {updated} updates. Resume tomorrow.")
            break

print(f"\n{'=' * 60}")
print(f"Updated: {updated}")
print(f"Errors:  {len(errors)}")

if errors:
    errors_file = Path(__file__).resolve().parent.parent / "analytics" / "rename-errors.json"
    errors_file.write_text(json.dumps(errors, indent=2))
    print(f"Errors saved to {errors_file}")
