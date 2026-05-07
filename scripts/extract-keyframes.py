"""Extract evenly-spaced keyframes from a video for content verification.

Usage:
    python scripts/extract-keyframes.py <video.mp4> [num_frames] [out_dir]

Defaults: 6 frames, written next to the video as <stem>_frame_NN.jpg.
"""
import sys
from pathlib import Path

import av

video = Path(sys.argv[1]).resolve()
num_frames = int(sys.argv[2]) if len(sys.argv) > 2 else 6
out_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else video.parent

with av.open(str(video)) as container:
    stream = container.streams.video[0]
    duration_s = float(container.duration) / av.time_base if container.duration else 0
    targets = [duration_s * (i + 1) / (num_frames + 1) for i in range(num_frames)]
    print(f"{video.name} duration={duration_s:.2f}s, extracting {num_frames} frames at {[f'{t:.1f}' for t in targets]}")

    target_idx = 0
    written = 0
    for frame in container.decode(stream):
        if target_idx >= len(targets):
            break
        if frame.time >= targets[target_idx]:
            out_path = out_dir / f"{video.stem}_frame_{target_idx + 1:02d}_t{frame.time:.1f}s.jpg"
            frame.to_image().save(out_path, quality=85)
            print(f"  wrote {out_path.name}")
            written += 1
            target_idx += 1

print(f"Extracted {written} frames to {out_dir}")
