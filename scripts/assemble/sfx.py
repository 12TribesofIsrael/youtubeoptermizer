"""
SFX library resolver.

Reads sfx_map.json and resolves each scene's sfx field to a local MP3 path.
No API calls — library files are downloaded once from Pixabay and cached locally.

If a file is missing, logs a warning and skips SFX for that scene so the
render continues without failing.
"""
import json
from pathlib import Path

_HERE = Path(__file__).parent
SFX_LIB_DIR = _HERE / "sfx_library"
SFX_MAP_PATH = _HERE / "sfx_map.json"

_sfx_map: dict | None = None


def _load_map() -> dict:
    global _sfx_map
    if _sfx_map is None:
        with open(SFX_MAP_PATH, encoding="utf-8") as f:
            _sfx_map = json.load(f)
    return _sfx_map


def default_volume() -> float:
    return _load_map().get("default_volume", 0.12)


def resolve_sfx(scene: dict) -> tuple[Path | None, float]:
    """
    Return (sfx_path, volume) for this scene.
    Returns (None, 0.0) if:
      - scene has no 'sfx' key (not tagged)
      - the library file doesn't exist yet (not downloaded)
    """
    sfx = scene.get("sfx")
    if not sfx:
        return None, 0.0

    filename = sfx.get("file")
    if not filename:
        return None, 0.0

    file_path = SFX_LIB_DIR / filename
    if not file_path.exists():
        print(
            f"  [sfx] MISSING: {filename} not in sfx_library/ — "
            f"skipping SFX for scene {scene['scene_id']}. "
            f"Download from Pixabay and save to {SFX_LIB_DIR}"
        )
        return None, 0.0

    volume = sfx.get("volume", default_volume())
    return file_path, volume


def list_missing(scenes: list[dict]) -> list[str]:
    """Return filenames that are tagged but not yet downloaded."""
    missing = []
    for scene in scenes:
        sfx = scene.get("sfx", {})
        filename = sfx.get("file")
        if filename and not (SFX_LIB_DIR / filename).exists():
            if filename not in missing:
                missing.append(filename)
    return missing


def print_download_guide(scenes: list[dict]) -> None:
    """Print a shopping list of missing SFX files with Pixabay search hints."""
    sfx_map = _load_map()
    moods = sfx_map.get("moods", {})
    missing = list_missing(scenes)
    if not missing:
        return

    print("\n[sfx] Files needed — download from pixabay.com/sound-effects/")
    print(f"      Save all to: {SFX_LIB_DIR}\n")
    for filename in missing:
        # Find the mood entry for this file
        mood_entry = next(
            (m for m in moods.values() if m.get("file") == filename), None
        )
        if mood_entry:
            print(f"  {filename}")
            print(f"    Search: \"{mood_entry['pixabay_query']}\"")
            print(f"    Use for: {mood_entry['description']}\n")
        else:
            print(f"  {filename}  (no Pixabay hint available)\n")
