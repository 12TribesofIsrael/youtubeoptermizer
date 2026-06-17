"""
Tag scenes in a clips_manifest.json with SFX mood assignments from the local library.

Reads each scene's 'prompt' (Kling visual description) and 'narration_text',
keyword-matches to a mood category from sfx_map.json, and writes the sfx field
back into the manifest.

Usage:
  python scripts/tag-sfx.py --manifest output/manifests/topic.json
  python scripts/tag-sfx.py --manifest output/manifests/topic.json --dry-run
  python scripts/tag-sfx.py --manifest output/manifests/topic.json --out output/manifests/topic-sfx.json

Output: overwrites the manifest in-place (or --out path) with sfx fields added.
Run assemble-video.py after this.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from assemble.sfx import SFX_MAP_PATH, SFX_LIB_DIR, print_download_guide


def load_sfx_map() -> dict:
    with open(SFX_MAP_PATH, encoding="utf-8") as f:
        return json.load(f)


def classify_mood(scene: dict, keyword_rules: list[list]) -> str:
    """
    Match scene text against keyword rules (first match wins).
    Falls back to 'golden-ambient' if nothing matches.

    Searches both 'prompt' (Kling visual cue) and 'narration_text'.
    """
    text = " ".join([
        scene.get("prompt", ""),
        scene.get("narration_text", ""),
    ]).lower()

    for rule in keyword_rules:
        mood, keywords = rule[0], rule[1]
        if not keywords:
            # Empty keyword list = catch-all default; skip in matching loop
            continue
        if any(kw.lower() in text for kw in keywords):
            return mood

    return "golden-ambient"


def tag_scenes(scenes: list[dict], sfx_map: dict, volume: float | None = None) -> list[dict]:
    moods = sfx_map["moods"]
    keyword_rules = sfx_map.get("keyword_rules", [])
    default_vol = volume if volume is not None else sfx_map.get("default_volume", 0.12)

    tagged = []
    for scene in scenes:
        scene = dict(scene)  # shallow copy — don't mutate original
        mood = classify_mood(scene, keyword_rules)

        # Walk fallback chain until we find a mood with a valid file entry
        visited = set()
        entry = moods.get(mood)
        while entry and mood not in visited:
            visited.add(mood)
            if entry.get("file"):
                break
            fallback = entry.get("fallback")
            if not fallback:
                break
            mood = fallback
            entry = moods.get(mood)

        if entry and entry.get("file"):
            scene["sfx"] = {
                "mood": mood,
                "file": entry["file"],
                "volume": default_vol,
            }
        tagged.append(scene)

    return tagged


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", required=True, help="Path to clips_manifest.json")
    parser.add_argument("--out", default=None,
                        help="Output path (default: overwrite manifest in-place)")
    parser.add_argument("--volume", type=float, default=None,
                        help="SFX volume 0.0–1.0 (default: from sfx_map.json, typically 0.12)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print mood assignments without writing the manifest")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.exists():
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path, encoding="utf-8") as f:
        data = json.load(f)

    sfx_map = load_sfx_map()
    scenes = data.get("scenes", [])

    tagged_scenes = tag_scenes(scenes, sfx_map, volume=args.volume)

    # Report
    print(f"\nSFX tagging: {len(scenes)} scenes\n")
    mood_counts: dict[str, int] = {}
    for scene in tagged_scenes:
        sfx = scene.get("sfx", {})
        mood = sfx.get("mood", "(none)")
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
        sid = scene.get("scene_id", "?")
        file = sfx.get("file", "(not tagged)")
        print(f"  Scene {sid:>3}: {mood:<20}  {file}")

    print(f"\nMood summary:")
    for mood, count in sorted(mood_counts.items(), key=lambda x: -x[1]):
        print(f"  {mood:<20} {count} scene(s)")

    # Show download guide for any missing files
    print_download_guide(tagged_scenes)

    if args.dry_run:
        print("\n[dry-run] No files written.")
        return

    data["scenes"] = tagged_scenes
    out_path = Path(args.out).resolve() if args.out else manifest_path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nManifest written -> {out_path}")
    print("Next: download missing SFX files, then run assemble-video.py.")


if __name__ == "__main__":
    main()
