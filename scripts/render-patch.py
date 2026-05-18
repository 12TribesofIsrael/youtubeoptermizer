"""
Surgical re-render: mix N fresh FLUX+Kling clips with reused ones + new narration.

When narration changes (e.g., fixed "theft" framing) or specific scenes need
a more descriptive prompt (e.g., Rebekah's womb scene), we don't want to
re-burn all 16 scenes. This script:

  1. Parses Kling URLs from a previous run's log (via simple regex match)
  2. Re-renders FLUX + Kling fresh for ONLY the scenes you specify
  3. Reuses the existing Kling URLs for all others
  4. Builds a fresh JSON2Video payload with the mix + new narration from
     the current scenes.json
  5. Submits and polls for the final MP4

Cost: (N fresh FLUX+Kling × per-scene-cost) + ~$1.50 JSON2Video, vs
~$6 for a full re-render at v1.6.

Usage:
  python scripts/render-patch.py \\
      --scenes output/scenes/edom-genesis49-part1-scenes.json \\
      --prev-log <path-to-previous-render-output-log> \\
      --redo 5,7,13 \\
      --kling-model v1.6
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

# Import the existing pipeline as a library — reuse its FLUX/Kling/JSON2Video
# helpers so we don't duplicate API logic.
PIPELINE_DIR = Path("C:/Users/Claude/ai-bible-gospels/workflows/custom-script")
sys.path.insert(0, str(PIPELINE_DIR))

# Load env from sibling .env
from dotenv import load_dotenv  # type: ignore
load_dotenv(PIPELINE_DIR.parent.parent / ".env")

# Force UTF-8 so any printed → / em-dash doesn't blow up on Windows cp1252
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Channel-locked Daniel voice (reference_daniel_voice.md)
DANIEL_VOICE_ID = "onwK4e9ZLuTAKqWW03F9"

# Regex matching the pipeline's per-scene completion log line
KLING_URL_RE = re.compile(r"\[(\d+)/\d+\] Video ready:\s*(https://\S+\.mp4)")


def parse_prev_log(log_path: Path) -> dict:
    """Extract {scene_index_1based: kling_url} from a previous run's output log."""
    text = log_path.read_text(encoding="utf-8", errors="replace")
    out = {}
    for m in KLING_URL_RE.finditer(text):
        out[int(m.group(1))] = m.group(2).rstrip(".")
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scenes", required=True,
                        help="Path to current scenes.json (output of script-to-scenes.py)")
    parser.add_argument("--prev-log", required=True,
                        help="Path to the previous render's full output log (contains Kling URLs)")
    parser.add_argument("--redo", required=True,
                        help="Comma-separated 1-based scene indices to re-render fresh (e.g., '5,7,13')")
    parser.add_argument("--kling-model", default="v1.6",
                        choices=["v1.6", "v2.1", "v3.0", "v3.0-pro", "o3", "o3-pro"])
    parser.add_argument("--voice-id", default=DANIEL_VOICE_ID)
    args = parser.parse_args()

    # Lazy-import pipeline helpers (only after sys.path is set + env loaded)
    import generate  # type: ignore

    scenes_path = Path(args.scenes).resolve()
    prev_log = Path(args.prev_log).resolve()
    redo_indices = sorted({int(x.strip()) for x in args.redo.split(",")})

    scenes = json.loads(scenes_path.read_text(encoding="utf-8"))["scenes"]
    prev_urls = parse_prev_log(prev_log)

    print(f"Loaded {len(scenes)} scenes from {scenes_path.name}")
    print(f"Parsed {len(prev_urls)} prior Kling URLs from {prev_log.name}")
    print(f"Re-render fresh: scenes {redo_indices}")
    print(f"Reuse from prev: scenes {sorted(set(range(1, len(scenes)+1)) - set(redo_indices))}")
    print()

    # Sanity: every non-redo scene must have a prior URL
    needed = set(range(1, len(scenes) + 1)) - set(redo_indices)
    missing = needed - set(prev_urls.keys())
    if missing:
        print(f"ERROR: prior log missing Kling URLs for scenes: {sorted(missing)}", file=sys.stderr)
        sys.exit(1)

    # Process scenes — fresh for redo, reuse for others
    processed = []
    total = len(scenes)
    for i, scene in enumerate(scenes, 1):
        if i in redo_indices:
            print(f"--- Scene {i}/{total} (FRESH) ---")
            image_url = generate.generate_image(scene, i, total)
            video_url = generate.generate_video(image_url, scene, i, total,
                                                kling_model=args.kling_model)
        else:
            video_url = prev_urls[i]
            print(f"--- Scene {i}/{total} (reused) -> {video_url[:70]}...")
        processed.append({
            "narration": scene["narration"],
            "video_url": video_url,
        })

    # Build + submit JSON2Video payload with new narration
    print(f"\nBuilding JSON2Video payload with voice {args.voice_id} ...")
    payload = generate.build_json2video_payload(processed, voice_id=args.voice_id)
    project_id = generate.submit_json2video(payload)
    mp4_url = generate.poll_json2video(project_id)

    print()
    print("=" * 60)
    print(f"DONE — patched render ready: {mp4_url}")
    print("=" * 60)


if __name__ == "__main__":
    main()
