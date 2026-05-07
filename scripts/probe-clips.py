"""Probe all clips in a directory and write duration / resolution / size to TSV.

Usage:
    python scripts/probe-clips.py [<clips-dir>] [<out.tsv>]

Defaults:
    clips-dir: faith-walk-live/anchor-doc/clips
    out.tsv:   faith-walk-live/anchor-doc/clip-durations.tsv

Uses PyAV (which ships its own libavformat) — no system ffmpeg dependency.
"""
import sys
from pathlib import Path

import av

ROOT = Path(__file__).resolve().parents[1]
clips_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "faith-walk-live/anchor-doc/clips"
out_tsv = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "faith-walk-live/anchor-doc/clip-durations.tsv"

clips = sorted(clips_dir.glob("*.mp4"), reverse=True)
print(f"Probing {len(clips)} clips in {clips_dir}")

rows = ["filename\tduration_s\twidth\theight\tsize_mb"]
for i, p in enumerate(clips, 1):
    try:
        with av.open(str(p)) as container:
            stream = container.streams.video[0]
            duration_s = float(container.duration) / av.time_base if container.duration else 0
            w, h = stream.codec_context.width, stream.codec_context.height
        size_mb = p.stat().st_size / (1024 * 1024)
        rows.append(f"{p.name}\t{duration_s:.2f}\t{w}\t{h}\t{size_mb:.2f}")
    except Exception as e:
        rows.append(f"{p.name}\tERROR\t-\t-\t-")
        print(f"  [{i}/{len(clips)}] ERROR on {p.name}: {e}")
    if i % 50 == 0:
        print(f"  {i}/{len(clips)} probed...")

out_tsv.write_text("\n".join(rows), encoding="utf-8")
print(f"\nWrote {out_tsv}")
print(f"Total clips: {len(clips)}")
