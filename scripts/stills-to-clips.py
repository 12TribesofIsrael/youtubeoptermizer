"""Convert still images (cards, archival stills, maps) into 1920x1080 H.264 MP4 clips
so they can be used as `clip_path` scenes in the FFmpeg assembler.

The assembler's Pass A stream-loops each clip to narration length. Static cards loop
invisibly. For Ken Burns stills we bake a slow zoom over a long duration (default 40s,
longer than any single Part-1 scene) so the loop rarely/never resets mid-scene.

Usage:
  python scripts/stills-to-clips.py IN.png OUT.mp4 [--motion static|kenburns-in|kenburns-out] [--dur 40]
Batch (a folder of PNGs -> sibling .mp4):
  python scripts/stills-to-clips.py --batch output/cards/eden-part1 --motion static --dur 6
"""
import argparse
import subprocess
import sys
from pathlib import Path

FPS = 30
W, H = 1920, 1080

# Two ways to reconcile a non-16:9 source with the frame:
#   pad  -> scale down, letterbox/pillarbox the remainder (nothing is lost, bars appear)
#   crop -> scale up, crop the overflow (fills the frame, edges are lost)
# 3:2 cards (1536x1024, what gpt-image-1 emits) pillarbox 150px per side under "pad",
# which visibly narrows the frame when cut against full-bleed Kling clips. "crop" matches
# them. Default stays "pad" — Part 1 was built and shipped with it.
FIT_PAD = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1"
FIT_CROP = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1"


def _vf(motion: str, dur: float, fit: str = "pad") -> str:
    frames = int(dur * FPS)
    if motion == "static":
        base = FIT_CROP if fit == "crop" else FIT_PAD
        return f"{base},fps={FPS}"
    # Ken Burns already fills the frame (scale-up + crop), so `fit` doesn't apply to it.
    # Ken Burns: upscale for headroom, then zoompan a slow push centered.
    if motion in ("kenburns-in", "kenburns", "zoom-in"):
        z = "min(zoom+0.0004,1.25)"
    elif motion in ("kenburns-out", "zoom-out"):
        z = "if(lte(zoom,1.0),1.25,max(zoom-0.0004,1.0))"
    else:  # pan-left / pan-right fall back to a gentle zoom for v1
        z = "min(zoom+0.0004,1.20)"
    return (
        f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,"
        f"crop={W*2}:{H*2},"
        f"zoompan=z='{z}':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS}"
    )


def convert(src: Path, dst: Path, motion: str, dur: float, fit: str = "pad"):
    vf = _vf(motion, dur, fit)
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(src), "-t", f"{dur}",
        "-vf", vf, "-r", str(FPS),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        str(dst),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ERROR {src.name}: {r.stderr[-400:]}")
        return False
    print(f"  {src.name} -> {dst.name}  ({motion}, {dur}s, {dst.stat().st_size/1024:.0f} KB)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?", help="input PNG")
    ap.add_argument("dst", nargs="?", help="output MP4")
    ap.add_argument("--batch", help="folder of PNGs -> sibling MP4s")
    ap.add_argument("--motion", default="static")
    ap.add_argument("--dur", type=float, default=40.0)
    ap.add_argument("--fit", choices=("pad", "crop"), default="pad",
                    help="how a non-16:9 still meets the frame; only affects --motion static")
    args = ap.parse_args()

    if args.batch:
        folder = Path(args.batch)
        pngs = sorted(folder.glob("*.png"))
        if not pngs:
            sys.exit(f"no PNGs in {folder}")
        print(f"Converting {len(pngs)} stills ({args.motion}, {args.dur}s)...")
        ok = sum(convert(p, p.with_suffix(".mp4"), args.motion, args.dur, args.fit) for p in pngs)
        print(f"Done: {ok}/{len(pngs)} clips.")
    else:
        if not args.src or not args.dst:
            sys.exit("provide IN.png OUT.mp4, or --batch FOLDER")
        convert(Path(args.src), Path(args.dst), args.motion, args.dur, args.fit)


if __name__ == "__main__":
    main()
