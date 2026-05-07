"""Probe ElevenLabs character balance and OpenAI usability.

Usage:
    python scripts/check-credits.py
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import requests

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
if not os.environ.get("ELEVENLABS_API_KEY"):
    load_dotenv(Path(__file__).resolve().parents[1].parent / "ai-bible-gospels" / ".env")

# --- ElevenLabs ---
el_key = os.environ.get("ELEVENLABS_API_KEY")
print("=== ElevenLabs ===")
if not el_key:
    print("  ELEVENLABS_API_KEY missing")
else:
    try:
        r = requests.get(
            "https://api.elevenlabs.io/v1/user/subscription",
            headers={"xi-api-key": el_key},
            timeout=15,
        )
        if r.status_code == 200:
            d = r.json()
            used = d.get("character_count", "?")
            limit = d.get("character_limit", "?")
            tier = d.get("tier", "?")
            remaining = (limit - used) if isinstance(used, int) and isinstance(limit, int) else "?"
            print(f"  tier={tier} used={used}/{limit} remaining={remaining}")
            print(f"  reset={d.get('next_character_count_reset_unix','?')}")
        else:
            print(f"  HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  ERROR: {e}")

# --- OpenAI (cheap probe — list models) ---
oa_key = os.environ.get("OPENAI_API_KEY")
print()
print("=== OpenAI ===")
if not oa_key:
    print("  OPENAI_API_KEY missing")
else:
    try:
        r = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {oa_key}"},
            timeout=15,
        )
        if r.status_code == 200:
            n = len(r.json().get("data", []))
            print(f"  /models OK ({n} models). Auth works. Quota check requires actual call.")
            # Tiny probe: 1-token completion to test quota
            r2 = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {oa_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 1,
                },
                timeout=30,
            )
            if r2.status_code == 200:
                print("  chat probe OK — quota available")
            else:
                print(f"  chat probe failed: HTTP {r2.status_code}: {r2.text[:200]}")
        else:
            print(f"  /models HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"  ERROR: {e}")
