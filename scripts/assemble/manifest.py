"""Load and validate clips_manifest.json; build per-topic output directories."""
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = ROOT / "output"


def load(manifest_path: Path) -> dict[str, Any]:
    """Load manifest, validate required fields, return dict."""
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    required_top = ("topic", "aspect", "voice_id", "scenes")
    for key in required_top:
        if key not in data:
            raise ValueError(f"Manifest missing required key: {key}")

    if data["aspect"] not in ("16x9", "9x16"):
        raise ValueError(f"aspect must be '16x9' or '9x16', got: {data['aspect']}")

    if not isinstance(data["scenes"], list) or len(data["scenes"]) == 0:
        raise ValueError("scenes must be a non-empty list")

    for i, scene in enumerate(data["scenes"]):
        for key in ("scene_id", "narration_text"):
            if key not in scene:
                raise ValueError(f"Scene {i} missing required key: {key}")
        # A scene's video source is either a Kling URL (downloaded) or a local
        # clip_path (archival/stock footage). Hybrid manifests mix both.
        if not scene.get("kling_url") and not scene.get("clip_path"):
            raise ValueError(
                f"Scene {i} ({scene.get('scene_id')}) needs either 'kling_url' or 'clip_path'"
            )

    return data


def build_dirs(topic: str) -> dict[str, Path]:
    """Create and return all per-topic output subdirectories."""
    dirs = {
        "clips":       OUTPUT_ROOT / "clips"       / topic,
        "audio":       OUTPUT_ROOT / "audio"       / topic,
        "subs":        OUTPUT_ROOT / "subs"        / topic,
        "scenes_tmp":  OUTPUT_ROOT / "scenes_tmp"  / topic,
        "renders":     OUTPUT_ROOT / "renders",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs
