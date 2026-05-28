"""
FFmpeg two-pass assembler.

Pass A: per-scene — loop clip to narration length, mux narration audio.
Pass B: concat all scenes + burn merged ASS subtitles.
"""
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Resolution and filter chains by aspect/strategy
SCALE_FILTERS = {
    "16x9": {
        "crop":     "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=30",
        "blur-pad": "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=30",
    },
    "9x16": {
        "crop":     "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30",
        "blur-pad": (
            "[v]scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,"
            "setsar=1,fps=30[vout]"
        ),
    },
}


def _ffmpeg_bin() -> str:
    """Resolve ffmpeg binary: FFMPEG_BIN env → tools/ffmpeg/bin → system PATH."""
    env_bin = os.environ.get("FFMPEG_BIN")
    if env_bin and Path(env_bin).exists():
        return env_bin
    bundled = ROOT / "tools" / "ffmpeg" / "bin" / "ffmpeg.exe"
    if bundled.exists():
        return str(bundled)
    return "ffmpeg"


def _escape_subtitle_path(p: Path) -> str:
    """
    Escape a subtitle path for FFmpeg's subtitles filter on Windows.
    Colons in drive letters must be backslash-escaped inside the filter string.
    E.g. C:/path/file.ass → C\\:/path/file.ass
    """
    s = str(p).replace("\\", "/")
    # Escape the colon in the drive letter (e.g. C: → C\:)
    if len(s) >= 2 and s[1] == ":":
        s = s[0] + "\\:" + s[2:]
    return s


def _run(cmd: list[str], label: str) -> None:
    """Run an ffmpeg command, streaming stderr to console. Raises on failure."""
    ffmpeg = _ffmpeg_bin()
    full_cmd = [ffmpeg] + cmd
    print(f"  ffmpeg [{label}]: {' '.join(full_cmd[:8])}...")
    result = subprocess.run(
        full_cmd,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        capture_output=False,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        print(result.stderr[-2000:], file=sys.stderr)
        raise RuntimeError(f"ffmpeg failed [{label}] with exit {result.returncode}")


def pass_a(
    scene_id: str,
    clip_path: Path,
    audio_path: Path,
    out_path: Path,
    aspect: str,
    vertical_strategy: str = "crop",
) -> Path:
    """
    Loop video clip to narration length, mux narration audio, normalize codec params.
    Identical codec output across all scenes is required for the concat demuxer in Pass B.
    """
    if out_path.exists():
        print(f"  [{scene_id}] Pass A cached: {out_path.name}")
        return out_path

    vf = SCALE_FILTERS[aspect][vertical_strategy]

    cmd = [
        "-y",
        "-stream_loop", "-1", "-i", str(clip_path),
        "-i", str(audio_path),
        "-map", "0:v:0", "-map", "1:a:0",
        "-vf", vf,
        "-af", "apad=pad_dur=0.2",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-shortest", "-fflags", "+genpts",
        str(out_path),
    ]
    _run(cmd, f"passA/{scene_id}")
    print(f"  [{scene_id}] Pass A done → {out_path.name}")
    return out_path


def pass_a_all(
    scenes: list[dict],
    clip_paths: dict[str, Path],
    audio_paths: dict[str, Path],
    scenes_tmp_dir: Path,
    aspect: str,
    vertical_strategy: str = "crop",
    max_workers: int = 2,
) -> dict[str, Path]:
    """Run Pass A for all scenes in parallel (max_workers=2 to avoid thrashing)."""
    print(f"Pass A: encoding {len(scenes)} scenes (up to {max_workers} parallel)...")
    results: dict[str, Path] = {}
    futures = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for scene in scenes:
            sid = scene["scene_id"]
            out_path = scenes_tmp_dir / f"scene_{sid}.mp4"
            fut = pool.submit(
                pass_a, sid, clip_paths[sid], audio_paths[sid], out_path, aspect, vertical_strategy
            )
            futures[fut] = sid
        for fut in as_completed(futures):
            sid = futures[fut]
            try:
                results[sid] = fut.result()
            except Exception as e:
                raise RuntimeError(f"Pass A failed for scene {sid}: {e}") from e

    # Assert scene ordering matches input scenes list
    ordered = [results[s["scene_id"]] for s in scenes]
    print(f"Pass A complete. {len(ordered)} scenes ready.\n")
    return results


def write_concat_list(scenes: list[dict], scene_paths: dict[str, Path], out_path: Path) -> Path:
    """Write FFmpeg concat demuxer file listing all scene MP4s in order.
    Uses absolute paths so FFmpeg doesn't resolve relative to the concat file's dir."""
    lines = []
    for scene in scenes:
        sid = scene["scene_id"]
        p = scene_paths[sid].resolve()
        lines.append(f"file '{str(p).replace(chr(92), '/')}'")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_path


def pass_b(
    concat_list: Path,
    ass_path: Path,
    fonts_dir: Path,
    out_path: Path,
) -> Path:
    """
    Concat all scenes and burn merged ASS subtitles.
    Audio is copied (already normalized in Pass A). Video re-encoded for subtitle burn.
    """
    if out_path.exists():
        out_path.unlink()

    sub_filter = (
        f"subtitles='{_escape_subtitle_path(ass_path)}'"
        f":fontsdir='{_escape_subtitle_path(fonts_dir)}'"
    )
    cmd = [
        "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-vf", sub_filter,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        str(out_path),
    ]
    _run(cmd, "passB/concat+subs")
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"Pass B complete -> {out_path.name} ({size_mb:.1f} MB)\n")
    return out_path
