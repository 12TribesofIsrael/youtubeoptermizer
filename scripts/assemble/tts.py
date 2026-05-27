"""Synthesize Daniel narration per scene via ElevenLabs API."""
import os
import sys
from pathlib import Path

import requests

DANIEL_VOICE_ID = "onwK4e9ZLuTAKqWW03F9"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"
VOICE_SETTINGS = {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.3,
    "use_speaker_boost": True,
}


def _get_api_key() -> str:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise RuntimeError(
            "ELEVENLABS_API_KEY not set. Add it to .env or "
            "ensure ai-bible-gospels/.env is loaded."
        )
    return key


def synthesize(
    text: str,
    out_path: Path,
    voice_id: str = DANIEL_VOICE_ID,
    model_id: str = DEFAULT_MODEL_ID,
    voice_speed: float = 0.9,
) -> Path:
    """Call ElevenLabs TTS and write MP3 to out_path. Returns out_path."""
    if out_path.exists():
        print(f"  TTS cached: {out_path.name}")
        return out_path

    api_key = _get_api_key()
    settings = {**VOICE_SETTINGS}
    if voice_speed != 1.0:
        settings["speed"] = voice_speed

    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={"text": text, "model_id": model_id, "voice_settings": settings},
        timeout=180,
    )
    if r.status_code != 200:
        try:
            detail = r.json()
        except Exception:
            detail = r.text[:300]
        raise RuntimeError(f"ElevenLabs HTTP {r.status_code}: {detail}")

    out_path.write_bytes(r.content)
    print(f"  TTS wrote {out_path.name} ({len(r.content)/1024:.1f} KB, {len(text)} chars)")
    return out_path


def synthesize_all(
    scenes: list[dict],
    audio_dir: Path,
    voice_id: str = DANIEL_VOICE_ID,
    model_id: str = DEFAULT_MODEL_ID,
    voice_speed: float = 0.9,
) -> dict[str, Path]:
    """Synthesize TTS for all scenes. Returns {scene_id: mp3_path}."""
    print(f"Synthesizing TTS for {len(scenes)} scenes (model: {model_id})...")
    results: dict[str, Path] = {}
    for scene in scenes:
        sid = scene["scene_id"]
        out_path = audio_dir / f"scene_{sid}.mp3"
        results[sid] = synthesize(
            scene["narration_text"], out_path, voice_id, model_id, voice_speed
        )
    print(f"TTS complete.\n")
    return results
