"""Transcribe all 7 anchor-doc narration MP3s into one combined subtitles file
with timestamps offset to match the documentary timeline.

Output: src/anchor-doc/src/subtitles.json — array of {start, end, text} cues
in absolute documentary seconds (not per-MP3 seconds).
"""
import json
import sys
from pathlib import Path

from faster_whisper import WhisperModel

# Narration MP3s with their planned start times in the documentary (seconds).
# Mirror src/anchor-doc/src/timeline.ts NARRATIONS exactly.
NARRATIONS = [
    {"file": "01_setup.mp3",          "start": 30},
    {"file": "02_beat1_setup.mp3",    "start": 102},
    {"file": "03_beat1_closeout.mp3", "start": 210},
    {"file": "04_beat2.mp3",          "start": 258},
    {"file": "05_beat3.mp3",          "start": 360},
    {"file": "06_beat4.mp3",          "start": 570},
    {"file": "07_cta.mp3",            "start": 750},
]

ROOT = Path(__file__).resolve().parents[1]
AUDIO_DIR = ROOT / "faith-walk-live" / "anchor-doc" / "audio"
OUT_PATH = ROOT / "src" / "anchor-doc" / "src" / "subtitles.json"

print("Loading Whisper base model...")
model = WhisperModel("base", device="cpu", compute_type="int8")

all_cues = []
for narration in NARRATIONS:
    audio_path = AUDIO_DIR / narration["file"]
    if not audio_path.exists():
        print(f"  WARN: {audio_path} not found, skipping")
        continue

    print(f"Transcribing {narration['file']} (offset {narration['start']}s)...")
    segments_iter, _ = model.transcribe(
        str(audio_path),
        word_timestamps=False,
        vad_filter=True,
        language="en",
    )

    offset = narration["start"]
    for seg in segments_iter:
        all_cues.append({
            "start": round(seg.start + offset, 2),
            "end": round(seg.end + offset, 2),
            "text": seg.text.strip(),
        })

print(f"\nWriting {len(all_cues)} cues to {OUT_PATH.relative_to(ROOT)}")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
OUT_PATH.write_text(json.dumps(all_cues, indent=2), encoding="utf-8")

print("Done.")
