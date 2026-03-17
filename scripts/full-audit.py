"""Pull all channel videos and flag issues for cleanup."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

client = YouTubeClient()

print("Fetching all videos from channel...")
videos = client.list_videos(max_results=300)
print(f"Found {len(videos)} videos\n")

# Categorize issues
handle_in_title = []
part_numbered = []
duplicates = {}
very_short = []
low_views = []
matthew6_flood = []

for v in videos:
    vid = v["id"]
    title = v["snippet"]["title"]
    desc = v["snippet"].get("description", "")
    published = v["snippet"]["publishedAt"]
    views = int(v["statistics"].get("viewCount", 0))
    duration_iso = v["contentDetails"]["duration"]  # e.g. PT45S, PT5M22S

    # Parse duration to seconds
    dur = duration_iso.replace("PT", "")
    seconds = 0
    if "H" in dur:
        h, dur = dur.split("H")
        seconds += int(h) * 3600
    if "M" in dur:
        m, dur = dur.split("M")
        seconds += int(m) * 60
    if "S" in dur:
        seconds += int(dur.replace("S", ""))

    entry = {
        "id": vid,
        "title": title,
        "views": views,
        "duration_sec": seconds,
        "published": published,
    }

    # Flag: @AIBIBLEGOSPELS in title
    if "@AIBIBLEGOSPELS" in title or "@aibiblegospels" in title.lower():
        handle_in_title.append(entry)

    # Flag: "Part X" titles
    if "Part " in title and ":" in title:
        part_numbered.append(entry)
        # Track duplicate part numbers
        import re
        match = re.search(r"Part\s+(\d+\.?\d*)", title)
        if match:
            part_num = match.group(1)
            duplicates.setdefault(part_num, []).append(entry)

    # Flag: Very short videos (<15 sec)
    if seconds < 15 and seconds > 0:
        very_short.append(entry)

    # Flag: Matthew 6 flood
    if "Matthew 6" in title or "Book of Matthew 6" in title:
        matthew6_flood.append(entry)

    # Flag: Low views (under 30)
    if views < 30:
        low_views.append(entry)

# Filter duplicates to only part numbers with 2+ videos
actual_dupes = {k: v for k, v in duplicates.items() if len(v) > 1}

print("=" * 60)
print("CHANNEL AUDIT REPORT")
print("=" * 60)

print(f"\n1. @AIBIBLEGOSPELS IN TITLE ({len(handle_in_title)} videos)")
print("   These titles get truncated in search results.")
for v in handle_in_title[:10]:
    print(f"   [{v['id']}] {v['title']} ({v['views']} views)")
if len(handle_in_title) > 10:
    print(f"   ... and {len(handle_in_title) - 10} more")

print(f"\n2. 'PART X' TITLES ({len(part_numbered)} videos)")
print("   Non-subscribers won't click these. Need standalone titles.")
for v in sorted(part_numbered, key=lambda x: x["views"], reverse=True)[:10]:
    print(f"   [{v['id']}] {v['title']} ({v['views']} views)")
if len(part_numbered) > 10:
    print(f"   ... and {len(part_numbered) - 10} more")

print(f"\n3. DUPLICATE PART NUMBERS ({len(actual_dupes)} part numbers with duplicates)")
for part_num, vids in sorted(actual_dupes.items(), key=lambda x: float(x[0])):
    print(f"   Part {part_num}:")
    for v in vids:
        print(f"     [{v['id']}] {v['title']} ({v['views']} views)")

print(f"\n4. MATTHEW 6 FLOOD ({len(matthew6_flood)} videos)")
for v in matthew6_flood:
    print(f"   [{v['id']}] {v['title']} ({v['views']} views)")

print(f"\n5. VERY SHORT VIDEOS <15sec ({len(very_short)} videos)")
for v in very_short:
    print(f"   [{v['id']}] {v['title']} ({v['duration_sec']}s, {v['views']} views)")

print(f"\n6. LOW PERFORMERS <30 VIEWS ({len(low_views)} videos)")
for v in sorted(low_views, key=lambda x: x["views"]):
    print(f"   [{v['id']}] {v['title']} ({v['views']} views)")

print(f"\n{'=' * 60}")
print("SUMMARY")
print(f"{'=' * 60}")
print(f"  Total videos:              {len(videos)}")
print(f"  @handle in title:          {len(handle_in_title)}")
print(f"  Part-numbered titles:      {len(part_numbered)}")
print(f"  Duplicate part numbers:    {len(actual_dupes)}")
print(f"  Matthew 6 flood:           {len(matthew6_flood)}")
print(f"  Very short (<15s):         {len(very_short)}")
print(f"  Low views (<30):           {len(low_views)}")

# Save full data for later use
output = Path(__file__).resolve().parent.parent / "analytics" / "audit-results.json"
audit_data = {
    "total_videos": len(videos),
    "handle_in_title": handle_in_title,
    "part_numbered": part_numbered,
    "duplicate_parts": {k: v for k, v in actual_dupes.items()},
    "matthew6_flood": matthew6_flood,
    "very_short": very_short,
    "low_views": low_views,
}
output.write_text(json.dumps(audit_data, indent=2))
print(f"\nFull audit data saved to {output}")
