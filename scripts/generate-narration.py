"""Generate Daniel narration for the anchor doc, beat by beat.

Usage:
    python scripts/generate-narration.py [beat_id]

If beat_id is provided, generate only that beat. Otherwise generate all beats.
Available beat IDs: setup, beat1_setup, beat1_closeout, beat2, beat3, beat4, cta

Output: faith-walk-live/anchor-doc/audio/<NN>_<beat_id>.mp3
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import requests

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
if not os.environ.get("ELEVENLABS_API_KEY"):
    load_dotenv(ROOT.parent / "ai-bible-gospels" / ".env")

API_KEY = os.environ["ELEVENLABS_API_KEY"]
DANIEL_VOICE_ID = "onwK4e9ZLuTAKqWW03F9"
MODEL_ID = "eleven_multilingual_v2"
OUT_DIR = ROOT / "faith-walk-live/anchor-doc/audio"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Voice settings tuned for documentary narration:
#   stability=0.5  -> measured but not robotic
#   similarity_boost=0.75 -> stay close to Daniel's broadcaster timbre
#   style=0.3 -> light expression, not theatrical
VOICE_SETTINGS = {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.3,
    "use_speaker_boost": True,
}

# Narration extracted from narration-script.md, stripped of stage directions.
# Each beat is a single ElevenLabs API call. Pauses are inserted via "..." or
# punctuation since narration-script timings are inferred from word count anyway.
BEATS = {
    "setup": (
        "01",
        "Setup (0:30 to 2:00)",
        (
            "On March 26, 2026, a man named Isaiah Thomas left Philadelphia with a backpack, "
            "a phone, and a plan most people would call impossible. Three thousand miles. "
            "East coast to California. On foot. ... Six weeks in, and still walking. "
            "His name is Isaiah Thomas. Most people on his stream call him Humble Zay. "
            "He's a minister out of Philly, and every step of this walk has been broadcast live, "
            "in real time, to a community of believers, supporters, and strangers watching from "
            "across the country. ... This is Faith Walk Live. ... Past Pennsylvania. Through Ohio. "
            "Through Indiana. Mile after mile, alone on the shoulder of state highways — "
            "and never alone, because the camera is always rolling, and the comments never stop. "
            "... But to understand what you're about to see, you have to understand why a man "
            "would do this. Three thousand miles. On foot. For something he hasn't built yet. "
            "So we'll let him explain it himself."
        ),
    ),
    "beat1_setup": (
        "02",
        "Beat 1 setup (2:00 to 2:30)",
        (
            "Faith Walk Live started as a question Zay was getting from everyone — strangers "
            "in gas stations, viewers in his stream, drivers slowing down on the shoulder. "
            "Why are you doing this? What's at the end of three thousand miles? "
            "... Here's how he answers it."
        ),
    ),
    "beat1_closeout": (
        "03",
        "Beat 1 close-out (3:30 to 4:25)",
        (
            "A school. A university. For kids who, in his words, 'end up in the system "
            "or end up dead.' ... He's not the first man to walk for his community's children. "
            "Sojourner Truth walked. Rosa Parks walked. Generations of Black men and women "
            "have walked, marched, and stood for what the next generation needed. ... "
            "But Zay is the first to broadcast every single step of it. The walk is the proof. "
            "The kids are the point. ... There's an old definition of religion that doesn't "
            "get quoted enough."
        ),
    ),
    "beat2": (
        "04",
        "Beat 2: The Road (4:35 to 7:00)",
        (
            "There is no romance in walking three thousand miles for a building that doesn't "
            "exist yet. It rains. It pours. The shoulder narrows. The trucks come close. "
            "Some days are twenty-six miles. Some days are thirty-seven. The body breaks "
            "down before the spirit does, and then the spirit has to carry the body the "
            "rest of the way. ... He sleeps where he can. Sometimes a stranger opens a door. "
            "Sometimes a parking lot. Sometimes a hotel paid for by a viewer he's never met. "
            "... A few weeks in, he was hit by a car. He went back to walking the next day. "
            "Started wearing a high-vis safety vest. By Day 39, he'd logged forty-one more "
            "miles since the impact. ... And every night, the stream comes back on. Every "
            "morning, the camera goes back up. The walk continues. The witness continues. "
            "... This is the part of the story you can't fake. You can stage a documentary. "
            "You can script a testimony. You cannot fake a thousand hours of livestream from "
            "the side of a highway in the rain. ... Faith Walk Live is real-time. "
            "It's auditable. It's happening right now, while you're watching this video."
        ),
    ),
    "beat3": (
        "05",
        "Beat 3: The Community (7:00 to 10:00)",
        (
            "And then something started happening. ... Strangers started showing up. "
            "... A grandmother in Indianapolis pulled over to bring him a hot meal. "
            "A brother in Ohio gifted him new shoes. A man named Terrance drove twenty "
            "miles out of his way just to walk a stretch with him. AirBnB hosts who'd never "
            "heard of him gave him rooms for free. ... These aren't actors. These aren't "
            "paid extras. These are real people — most of them Black, most of them strangers "
            "— deciding that one of their own is worth backing. ... That's what community "
            "investment looks like, when it's real. Not in theory. On a state highway in the "
            "Midwest. ... The school in Philly doesn't exist yet. But the people who'll build "
            "it are already showing up — every mile, every day, on Twitch."
        ),
    ),
    "beat4": (
        "06",
        "Beat 4: The Mission (10:00 to 12:00)",
        (
            "That's why we built faithwalklive.com. A live tracker. Real-time mile counter. "
            "Stream embed. Community feed. So no one has to scroll Twitch to know where "
            "Zay is, how many miles he's logged, who showed up today. ... At AI Bible Gospels, "
            "the tools we build — the trackers, the stream automation, the ministry sites — "
            "they exist for one reason. ... Software in service of the calling. ... "
            "Because what's happening on this walk is bigger than the walk itself. "
            "It's a proof of concept. That when a Black minister moves in faith — for his "
            "community, for his city, for the kids most of the world has written off — "
            "the body responds. People show up. Money comes in. The school gets built. "
            "... California is two thousand seven hundred miles from where he stands today. "
            "He's going to walk every one of them. And every step is a brick in a building "
            "that hasn't been built yet."
        ),
    ),
    "cta": (
        "07",
        "CTA / Closing (12:30 to 13:30)",
        (
            "If this stirred something in you, there are three things you can do right now. "
            "... One. Track the walk live at faithwalklive.com. Watch where Zay is, today, "
            "this minute. ... Two. Donate to the school. The GoFundMe link is below this "
            "video — every dollar goes to the school in Philly. ... Three. Subscribe to "
            "AI Bible Gospels. We tell stories like this — about ministers, missions, and "
            "the tools that serve the calling. ... One foot in front of the other. "
            "... That's all it takes."
        ),
    ),
}


def synthesize(beat_id: str) -> Path:
    num, label, text = BEATS[beat_id]
    char_count = len(text)
    print(f"[{num}] {label} — {char_count} chars")
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{DANIEL_VOICE_ID}",
        headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": MODEL_ID,
            "voice_settings": VOICE_SETTINGS,
        },
        timeout=180,
    )
    if r.status_code != 200:
        try:
            print(f"  ERROR HTTP {r.status_code}: {r.json()}")
        except Exception:
            print(f"  ERROR HTTP {r.status_code}: {r.text[:300]}")
        sys.exit(1)
    out_path = OUT_DIR / f"{num}_{beat_id}.mp3"
    out_path.write_bytes(r.content)
    print(f"  wrote {out_path.name} ({len(r.content)/1024:.1f} KB)")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) > 1:
        targets = [sys.argv[1]]
        if targets[0] not in BEATS:
            print(f"Unknown beat: {targets[0]}. Available: {list(BEATS.keys())}")
            sys.exit(1)
    else:
        targets = list(BEATS.keys())

    total_chars = sum(len(BEATS[b][2]) for b in targets)
    print(f"Synthesizing {len(targets)} beat(s), total {total_chars} chars")
    print()
    for b in targets:
        synthesize(b)
    print()
    print(f"Done. {len(targets)} mp3(s) in {OUT_DIR}")
