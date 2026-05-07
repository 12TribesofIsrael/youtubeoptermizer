"""Transcribe an mp4 locally via faster-whisper (no API, no credits).

Usage:
    python scripts/transcribe-reel.py <path/to/video.mp4> [out.json]

First run downloads the Whisper "base" model (~74MB) to the local cache.
Subsequent runs are fast. Word-level timestamps are saved as JSON for tight
Daniel narration timing.
"""
import sys
import json
from pathlib import Path

from faster_whisper import WhisperModel

video = Path(sys.argv[1]).resolve()
out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else video.with_suffix(".transcript.json")

print("Loading Whisper base model (first run downloads ~74MB)...")
model = WhisperModel("base", device="cpu", compute_type="int8")

print(f"Transcribing {video.name}...")
segments_iter, info = model.transcribe(
    str(video),
    word_timestamps=True,
    vad_filter=True,
    language="en",
)

segments = []
for seg in segments_iter:
    segments.append(
        {
            "start": seg.start,
            "end": seg.end,
            "text": seg.text,
            "words": [
                {"word": w.word, "start": w.start, "end": w.end, "probability": w.probability}
                for w in (seg.words or [])
            ],
        }
    )

full_text = " ".join(s["text"].strip() for s in segments)
out = {
    "language": info.language,
    "duration": info.duration,
    "text": full_text,
    "segments": segments,
}
out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"\nSaved transcript -> {out_path}")
print(f"Detected language: {info.language} (prob {info.language_probability:.2f})")
print(f"Audio duration: {info.duration:.2f}s")
print()
print("=== FULL TEXT ===")
print(full_text)
print()
print("=== SEGMENTS ===")
for s in segments:
    print(f"[{s['start']:6.2f} -> {s['end']:6.2f}] {s['text'].strip()}")
