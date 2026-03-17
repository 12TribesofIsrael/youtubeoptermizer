"""Retry transcript extraction for the 26 videos that failed due to IP block."""

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from youtube_transcript_api import YouTubeTranscriptApi

errors_file = Path(__file__).resolve().parent.parent / "analytics" / "transcript-errors.json"
errors = json.loads(errors_file.read_text())

print(f"Retrying transcripts for {len(errors)} videos...")
print("=" * 60)

ytt_api = YouTubeTranscriptApi()
results = []
still_failed = []

for i, entry in enumerate(errors):
    vid = entry["id"]
    part_num = entry["part_num"]

    try:
        transcript = ytt_api.fetch(vid)
        full_text = " ".join(snippet.text for snippet in transcript)
        results.append({
            "id": vid,
            "part_num": part_num,
            "old_title": entry["old_title"],
            "views": entry["views"],
            "transcript_preview": full_text[:500],
            "full_transcript": full_text,
        })
        print(f"  [{i+1}/{len(errors)}] Part {part_num} ({vid}) — {len(full_text)} chars")
        time.sleep(1)
    except Exception as e:
        still_failed.append(entry)
        print(f"  [{i+1}/{len(errors)}] Part {part_num} ({vid}) — FAILED: {str(e)[:80]}")
        time.sleep(2)

output = Path(__file__).resolve().parent.parent / "analytics" / "part-topics-batch2.json"
output.write_text(json.dumps(results, indent=2, ensure_ascii=False))

print(f"\nExtracted: {len(results)}")
print(f"Still failed: {len(still_failed)}")
print(f"Saved to {output}")
