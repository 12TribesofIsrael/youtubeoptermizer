"""Extract transcripts from all Part-titled videos to determine their topics."""

import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from youtube_transcript_api import YouTubeTranscriptApi

# Load audit data and filter to Part videos, excluding deleted ones
audit_file = Path(__file__).resolve().parent.parent / "analytics" / "audit-results.json"
audit = json.loads(audit_file.read_text())

# IDs we deleted in Phase 1
deleted_ids = {
    "_VyT3Wja8rI", "Iu9j9lbO1L0", "7lEXIjb1w8c", "OP8DH3QeOlM",
    "CoqyWeGFwik", "_zhWsE36dss", "Mgkob7zPCXg", "MAkhk-cIuvE",
    "QTsCcJxRhsc", "sbv8oJWTgHk", "8o0oDlRCAKc",
}

parts = [p for p in audit["part_numbered"] if p["id"] not in deleted_ids]
parts.sort(key=lambda x: x["views"], reverse=True)

print(f"Extracting transcripts for {len(parts)} Part videos...")
print("=" * 60)

results = []
errors = []

ytt_api = YouTubeTranscriptApi()

for i, p in enumerate(parts):
    vid = p["id"]
    title = p["title"]
    part_match = re.search(r"Part\s+(\d+\.?\d*)", title)
    part_num = part_match.group(1) if part_match else "?"

    try:
        transcript = ytt_api.fetch(vid)
        # Combine all text segments
        full_text = " ".join(snippet.text for snippet in transcript)
        # Take first 500 chars as topic summary
        summary = full_text[:500]

        results.append({
            "id": vid,
            "part_num": part_num,
            "old_title": title,
            "views": p["views"],
            "transcript_preview": summary,
            "full_transcript": full_text,
        })
        print(f"  [{i+1}/{len(parts)}] Part {part_num} ({vid}) — {len(full_text)} chars")
    except Exception as e:
        errors.append({"id": vid, "part_num": part_num, "old_title": title, "views": p["views"], "error": str(e)})
        print(f"  [{i+1}/{len(parts)}] Part {part_num} ({vid}) — ERROR: {e}")

# Save results
output = Path(__file__).resolve().parent.parent / "analytics" / "part-topics.json"
output.write_text(json.dumps(results, indent=2, ensure_ascii=False))

errors_file = Path(__file__).resolve().parent.parent / "analytics" / "transcript-errors.json"
if errors:
    errors_file.write_text(json.dumps(errors, indent=2))

print(f"\n{'=' * 60}")
print(f"Transcripts extracted: {len(results)}")
print(f"Errors: {len(errors)}")
print(f"Saved to {output}")
