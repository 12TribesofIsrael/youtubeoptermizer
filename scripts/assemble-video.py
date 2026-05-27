"""
Local FFmpeg assembler — replaces JSON2Video as the last-mile step.

Ingests a clips_manifest.json (produced by ai-bible-gospels generate.py
--skip-json2video) and outputs a branded MP4: looped Kling clips, Daniel TTS
narration, and Approach-B ASS karaoke subtitles (yellow current word, gray others).

Usage:
  python scripts/assemble-video.py --manifest output/manifests/topic.json
  python scripts/assemble-video.py --manifest tests/fixtures/canary_manifest.json --scenes 1 --keep-intermediates

See docs/local-ffmpeg-assembler.md for full spec, risk list, and canary protocol.
"""
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
if not os.environ.get("ELEVENLABS_API_KEY"):
    load_dotenv(ROOT.parent / "ai-bible-gospels" / ".env")

# Add scripts/ to path so `assemble` package is importable
sys.path.insert(0, str(ROOT / "scripts"))

from assemble import manifest as manifest_mod
from assemble.download_clips import download_all
from assemble.tts import synthesize_all
from assemble.transcribe import transcribe_all
from assemble.durations import probe
from assemble.ass_writer import write_merged_ass
from assemble.ffmpeg_build import pass_a_all, write_concat_list, pass_b

FONTS_DIR = ROOT / "scripts" / "assemble" / "fonts"
DANIEL_VOICE_ID = "onwK4e9ZLuTAKqWW03F9"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", required=True,
                        help="Path to clips_manifest.json")
    parser.add_argument("--aspect", choices=("16x9", "9x16"),
                        help="Override aspect ratio from manifest")
    parser.add_argument("--vertical-strategy", choices=("crop", "blur-pad"), default="crop",
                        help="How to convert 16:9 Kling clips to 9:16 (default: crop)")
    parser.add_argument("--scenes", type=int, default=None, metavar="N",
                        help="Process only the first N scenes (canary mode)")
    parser.add_argument("--keep-intermediates", action="store_true",
                        help="Keep clips/, audio/, subs/, scenes_tmp/ after success")
    parser.add_argument("--whisper-model", default="base", choices=("tiny", "base", "small", "small.en", "medium"),
                        help="Whisper model size (default: base; upgrade to small.en if KJV timing is poor)")
    parser.add_argument("--tts-model", default=DEFAULT_MODEL_ID,
                        help=f"ElevenLabs model (default: {DEFAULT_MODEL_ID})")
    parser.add_argument("--voice-id", default=DANIEL_VOICE_ID,
                        help=f"ElevenLabs voice ID (default: Daniel {DANIEL_VOICE_ID})")
    parser.add_argument("--voice-speed", type=float, default=0.9,
                        help="Voice speed (default: 0.9 — slightly slower for KJV clarity)")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.exists():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    # --- Load & validate manifest ---
    data = manifest_mod.load(manifest_path)
    topic = data["topic"]
    aspect = args.aspect or data["aspect"]
    voice_id = data.get("voice_id", args.voice_id)
    voice_speed = data.get("voice_speed", args.voice_speed)

    scenes = data["scenes"]
    if args.scenes is not None:
        scenes = scenes[:args.scenes]
        print(f"Canary mode: processing first {len(scenes)} scene(s).\n")

    print(f"Assembling topic='{topic}' aspect={aspect} scenes={len(scenes)}")
    print(f"  voice={voice_id}  speed={voice_speed}  tts_model={args.tts_model}\n")

    # --- Create output dirs ---
    dirs = manifest_mod.build_dirs(topic)

    # --- Phase 1: Download Kling clips (before TTS — signed URLs expire) ---
    clip_paths = download_all(scenes, dirs["clips"])

    # --- Phase 2: TTS ---
    audio_paths = synthesize_all(
        scenes, dirs["audio"], voice_id, args.tts_model, voice_speed
    )

    # --- Phase 3: Whisper word timestamps ---
    words_by_scene = transcribe_all(scenes, audio_paths, args.whisper_model)

    # --- Phase 4: Probe audio durations for subtitle offsets ---
    audio_durations = {
        sid: probe(audio_paths[sid])["duration_s"]
        for sid in audio_paths
    }

    # --- Phase 5: Write merged ASS ---
    ass_path = dirs["subs"] / "merged.ass"
    write_merged_ass(scenes, words_by_scene, audio_durations, ass_path, aspect)
    print(f"Subtitles written → {ass_path.name}\n")

    # --- Phase 6: Pass A (per-scene encode) ---
    scene_paths = pass_a_all(
        scenes, clip_paths, audio_paths, dirs["scenes_tmp"],
        aspect, args.vertical_strategy
    )

    # --- Phase 7: Write concat list ---
    concat_list = dirs["scenes_tmp"] / "concat_list.txt"
    write_concat_list(scenes, scene_paths, concat_list)

    # --- Phase 8: Pass B (concat + subtitle burn) ---
    suffix = f"_{args.scenes}scene" if args.scenes is not None else ""
    out_path = dirs["renders"] / f"{topic}{suffix}.mp4"
    pass_b(concat_list, ass_path, FONTS_DIR, out_path)

    print(f"Done. Output: {out_path}")

    # --- Cleanup intermediates ---
    if not args.keep_intermediates:
        import shutil
        for key in ("clips", "audio", "subs", "scenes_tmp"):
            d = dirs[key]
            if d.exists():
                shutil.rmtree(d)
                print(f"  Cleaned {d.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
