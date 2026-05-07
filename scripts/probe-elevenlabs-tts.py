"""Tiny TTS probe to verify ElevenLabs Daniel voice is available."""
import os
from pathlib import Path

from dotenv import load_dotenv
import requests

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
if not os.environ.get("ELEVENLABS_API_KEY"):
    load_dotenv(Path(__file__).resolve().parents[1].parent / "ai-bible-gospels" / ".env")

key = os.environ["ELEVENLABS_API_KEY"]
voice_id = "onwK4e9ZLuTAKqWW03F9"  # Daniel - Steady Broadcaster

r = requests.post(
    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
    headers={"xi-api-key": key, "Content-Type": "application/json"},
    json={"text": "Hello.", "model_id": "eleven_multilingual_v2"},
    timeout=30,
)

print(f"HTTP {r.status_code}")
if r.status_code == 200:
    out = Path(__file__).resolve().parents[1] / "faith-walk-live/anchor-doc/_tts_probe.mp3"
    out.write_bytes(r.content)
    print(f"OK — wrote {len(r.content)} bytes to {out}")
else:
    try:
        print(r.json())
    except Exception:
        print(r.text[:400])
