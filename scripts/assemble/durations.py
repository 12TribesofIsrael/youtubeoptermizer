"""Probe video/audio file durations and resolution using PyAV (no system ffmpeg)."""
from pathlib import Path

import av


def probe(path: Path) -> dict:
    """Return {duration_s, width, height} for a video or audio file."""
    with av.open(str(path)) as container:
        duration_s = float(container.duration) / av.time_base if container.duration else 0.0
        width, height = 0, 0
        if container.streams.video:
            stream = container.streams.video[0]
            width = stream.codec_context.width
            height = stream.codec_context.height
    return {"duration_s": duration_s, "width": width, "height": height}
