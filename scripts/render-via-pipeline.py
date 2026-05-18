"""
Thin wrapper around ai-bible-gospels' custom-script generate.py CLI.

Saves typing the full pipeline path and the channel-locked Daniel voice ID
on every render. Pure subprocess shell-out — no monkey-patching.

The pipeline ships in C:/Users/Claude/ai-bible-gospels (separate repo, read-only
from this workspace except for the scoped --voice-id flag added on 2026-05-16).

Usage:
  python scripts/render-via-pipeline.py output/scenes/edom-genesis49-part1-scenes.json
  python scripts/render-via-pipeline.py output/scenes/edom-part1-scenes.json --scenes-only
  python scripts/render-via-pipeline.py output/scenes/test.json --voice-id <other-id>
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

PIPELINE_DIR = Path("C:/Users/Claude/ai-bible-gospels/workflows/custom-script")
# Daniel Steady Broadcaster — channel-locked viral voice (reference_daniel_voice.md)
DEFAULT_VOICE_ID = "onwK4e9ZLuTAKqWW03F9"
KLING_MODELS = ("v1.6", "v2.1", "v3.0", "v3.0-pro", "o3", "o3-pro")
DEFAULT_KLING_MODEL = "v3.0"

# Auto-loaded LoRA config (written by scripts/train-flux-lora.py)
LORA_CONFIG_PATH = Path(__file__).resolve().parent.parent / "training" / "lora-config.json"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("scenes_json", help="Path to scenes.json file emitted by script-to-scenes.py")
    parser.add_argument("--voice-id", default=DEFAULT_VOICE_ID,
                        help=f"ElevenLabs voice override (default: Daniel {DEFAULT_VOICE_ID})")
    parser.add_argument("--kling-model", default=DEFAULT_KLING_MODEL, choices=KLING_MODELS,
                        help=f"Kling model variant (default {DEFAULT_KLING_MODEL}). "
                             "v1.6 = cheapest test, o3-pro = best quality.")
    parser.add_argument("--scenes-only", action="store_true",
                        help="Forward --scenes-only to generate.py — skips FLUX/Kling/JSON2Video (zero cost)")
    parser.add_argument("--post-produce", action="store_true",
                        help="Forward --post-produce to generate.py — runs intro/outro/logo overlay")
    parser.add_argument("--no-lora", action="store_true",
                        help="Skip LoRA even if training/lora-config.json exists")
    parser.add_argument("--lora-url", default=None,
                        help="Override the LoRA URL from training/lora-config.json")
    parser.add_argument("--lora-trigger", default=None,
                        help="Override the LoRA trigger word from training/lora-config.json")
    parser.add_argument("--lora-scale", type=float, default=1.0,
                        help="LoRA strength (default 1.0)")
    args = parser.parse_args()

    # Auto-load LoRA config if present and not overridden
    lora_url = args.lora_url
    lora_trigger = args.lora_trigger
    if not args.no_lora and LORA_CONFIG_PATH.exists():
        cfg = json.loads(LORA_CONFIG_PATH.read_text(encoding="utf-8"))
        lora_url = lora_url or cfg.get("lora_url")
        lora_trigger = lora_trigger or cfg.get("trigger_word")
        if lora_url and lora_trigger:
            print(f"  LoRA: {lora_trigger} -> {lora_url[:70]}...")

    scenes_path = Path(args.scenes_json).resolve()
    if not scenes_path.exists():
        print(f"ERROR: {scenes_path} not found", file=sys.stderr)
        sys.exit(1)
    if scenes_path.suffix != ".json":
        print(f"ERROR: expected .json file, got {scenes_path.suffix}", file=sys.stderr)
        sys.exit(1)

    if not PIPELINE_DIR.exists():
        print(f"ERROR: pipeline dir not found: {PIPELINE_DIR}", file=sys.stderr)
        print("If ai-bible-gospels lives elsewhere, edit PIPELINE_DIR in this script.", file=sys.stderr)
        sys.exit(1)

    cmd = [
        sys.executable, "generate.py", str(scenes_path),
        "--voice-id", args.voice_id,
        "--kling-model", args.kling_model,
    ]
    if lora_url and lora_trigger:
        cmd.extend(["--lora-url", lora_url, "--lora-trigger", lora_trigger,
                    "--lora-scale", str(args.lora_scale)])
    if args.scenes_only:
        cmd.append("--scenes-only")
    if args.post_produce:
        cmd.append("--post-produce")

    print(f"Running: {' '.join(cmd)}")
    print(f"  cwd: {PIPELINE_DIR}\n")

    # Force UTF-8 stdout so generate.py's print() of "→" doesn't blow up on
    # Windows cp1252 console (Python 3.14 default on Windows).
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    result = subprocess.run(cmd, cwd=PIPELINE_DIR, env=env)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
