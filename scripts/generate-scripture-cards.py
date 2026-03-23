"""
Generate all 58 Deuteronomy 28 scripture cards using OpenAI DALL-E API.
Outputs 1792x1024 PNG images to output/scripture-cards/

Usage:
    set OPENAI_API_KEY=your-key-here
    python scripts/generate-scripture-cards.py

Or generate a single card:
    python scripts/generate-scripture-cards.py --card 34
"""

import os
import sys
import time
import requests
from pathlib import Path
from openai import OpenAI

# ── Config ──────────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "scripture-cards"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── All 58 Cards ────────────────────────────────────────────────────────
CARDS = [
    # Scene 1 — Cold Open
    {"id": 1, "type": "question", "text": "Who was Christ?"},
    {"id": 2, "type": "question", "text": "Which bloodline?"},
    {"id": 3, "type": "question", "text": "Which tribe?"},
    {"id": 4, "type": "question", "text": "What did he look like?"},
    {"id": 5, "type": "title", "text": "DEUTERONOMY 28\nEVERY CURSE THAT CAME TRUE\n\nAI BIBLE GOSPELS"},
    {"id": 6, "type": "scripture", "text": '"But it shall come to pass, if thou wilt not hearken unto the voice of the LORD thy God... that all these curses shall come upon thee, and overtake thee."\n\n— Deuteronomy 28:15'},

    # Scene 2 — Cursed in City/Field
    {"id": 7, "type": "scripture", "text": '"Cursed shalt thou be in the city, and cursed shalt thou be in the field."\n\n— Deuteronomy 28:16'},
    {"id": 8, "type": "scripture", "text": '"Cursed shall be thy basket and thy store. Cursed shall be the fruit of thy body, and the fruit of thy land."\n\n— Deuteronomy 28:17-18'},

    # Scene 3 — Pestilence, Madness
    {"id": 9, "type": "scripture", "text": '"The LORD shall make the pestilence cleave unto thee... the LORD shall smite thee with a consumption, and with a fever, and with an inflammation."\n\n— Deuteronomy 28:21-22'},
    {"id": 10, "type": "scripture", "text": '"The LORD shall smite thee with madness, and blindness, and astonishment of heart. And thou shalt grope at noonday, as the blind gropeth in darkness."\n\n— Deuteronomy 28:28-29'},
    {"id": 11, "type": "scripture", "text": '"Thou shalt not prosper in thy ways: and thou shalt be only oppressed and spoiled evermore, and no man shall save thee."\n\n— Deuteronomy 28:29'},

    # Scene 4 — Wife, Children, Labor
    {"id": 12, "type": "scripture", "text": '"Thou shalt betroth a wife, and another man shall lie with her. Thou shalt build an house, and thou shalt not dwell therein."\n\n— Deuteronomy 28:30'},
    {"id": 13, "type": "scripture", "text": '"Thy sons and thy daughters shall be given unto another people, and thine eyes shall look, and fail with longing for them all the day long: and there shall be no might in thine hand."\n\n— Deuteronomy 28:32'},
    {"id": 14, "type": "scripture", "text": '"The fruit of thy land, and all thy labours, shall a nation which thou knowest not eat up."\n\n— Deuteronomy 28:33'},
    {"id": 15, "type": "scripture", "text": '"Thou shalt beget sons and daughters, but thou shalt not enjoy them; for they shall go into captivity."\n\n— Deuteronomy 28:41'},

    # Scene 5 — Byword
    {"id": 16, "type": "scripture", "text": '"And thou shalt become an astonishment, a proverb, and a byword, among all nations whither the LORD shall lead thee."\n\n— Deuteronomy 28:37'},
    {"id": 17, "type": "byword", "text": "NEGRO."},
    {"id": 18, "type": "byword", "text": "COLORED."},
    {"id": 19, "type": "byword", "text": "AFRICAN AMERICAN."},
    {"id": 20, "type": "byword", "text": "MEXICAN."},
    {"id": 21, "type": "byword", "text": "INDIAN."},
    {"id": 22, "type": "byword", "text": "WEST INDIAN."},
    {"id": 23, "type": "byword", "text": "ABORIGINAL."},
    {"id": 24, "type": "byword", "text": "LATINO."},
    {"id": 25, "type": "byword", "text": "MINORITY."},
    {"id": 26, "type": "byword_final", "text": "ISRAELITE."},
    {"id": 27, "type": "scripture", "text": '"The stranger that is within thee shall get up above thee very high; and thou shalt come down very low. He shall lend to thee, and thou shalt not lend to him: he shall be the head, and thou shalt be the tail."\n\n— Deuteronomy 28:43-44'},

    # Scene 6 — Yoke of Iron
    {"id": 28, "type": "scripture", "text": '"Therefore shalt thou serve thine enemies... in hunger, and in thirst, and in nakedness, and in want of all things: and he shall put a yoke of iron upon thy neck."\n\n— Deuteronomy 28:48'},
    {"id": 29, "type": "emphasis", "text": "A YOKE OF IRON"},

    # Scene 7 — Eagle Nation
    {"id": 30, "type": "scripture", "text": '"The LORD shall bring a nation against thee from far, from the end of the earth, as swift as the eagle flieth; a nation whose tongue thou shalt not understand."\n\n— Deuteronomy 28:49'},
    {"id": 31, "type": "scripture", "text": '"A nation of fierce countenance, which shall not regard the person of the old, nor shew favour to the young."\n\n— Deuteronomy 28:50'},

    # Scene 8 — Scattered
    {"id": 32, "type": "scripture", "text": '"And the LORD shall scatter thee among all people, from the one end of the earth even unto the other."\n\n— Deuteronomy 28:64'},
    {"id": 33, "type": "scripture", "text": '"Among these nations shalt thou find no ease... the LORD shall give thee there a trembling heart, and failing of eyes, and sorrow of mind. And thy life shall hang in doubt before thee; and thou shalt fear day and night."\n\n— Deuteronomy 28:65-67'},

    # Scene 9 — Ships
    {"id": 34, "type": "scripture", "text": '"And the LORD shall bring thee into Egypt again with ships... and there ye shall be sold unto your enemies for bondmen and bondwomen, and no man shall buy you."\n\n— Deuteronomy 28:68'},

    # Scene 10 — Verdict
    {"id": 35, "type": "scripture", "text": '"And they shall be upon thee for a sign and for a wonder, and upon thy seed for ever."\n\n— Deuteronomy 28:46'},
    {"id": 36, "type": "verdict", "text": "Cursed in the city. ✓"},
    {"id": 37, "type": "verdict", "text": "Cursed in the field. ✓"},
    {"id": 38, "type": "verdict", "text": "Pestilence. ✓"},
    {"id": 39, "type": "verdict", "text": "Fever. ✓"},
    {"id": 40, "type": "verdict", "text": "Madness and blindness. ✓"},
    {"id": 41, "type": "verdict", "text": "Wife taken. ✓"},
    {"id": 42, "type": "verdict", "text": "Children stolen. ✓"},
    {"id": 43, "type": "verdict", "text": "Labor consumed. ✓"},
    {"id": 44, "type": "verdict", "text": "A byword among nations. ✓"},
    {"id": 45, "type": "verdict", "text": "The stranger above you. ✓"},
    {"id": 46, "type": "verdict", "text": "A yoke of iron. ✓"},
    {"id": 47, "type": "verdict", "text": "The eagle nation. ✓"},
    {"id": 48, "type": "verdict", "text": "A tongue you don't understand. ✓"},
    {"id": 49, "type": "verdict", "text": "Scattered to the ends of the earth. ✓"},
    {"id": 50, "type": "verdict", "text": "No ease among the nations. ✓"},
    {"id": 51, "type": "verdict", "text": "Life hanging in doubt. ✓"},
    {"id": 52, "type": "verdict", "text": "Ships. ✓"},
    {"id": 53, "type": "verdict", "text": "Sold as slaves. ✓"},
    {"id": 54, "type": "verdict", "text": "No man shall buy you. ✓"},

    # Closing
    {"id": 55, "type": "scripture", "text": '"All these curses shall come upon thee, and overtake thee."\n\n— Deuteronomy 28:15'},
    {"id": 56, "type": "scripture", "text": '"They shall be upon thee for a sign and for a wonder, and upon thy seed for ever."\n\n— Deuteronomy 28:46'},
    {"id": 57, "type": "scripture", "text": '"Then the LORD thy God will turn thy captivity, and have compassion upon thee."\n\n— Deuteronomy 30:3'},
    {"id": 58, "type": "logo", "text": "AI BIBLE GOSPELS"},
]


def build_prompt(card):
    """Build a DALL-E prompt based on card type."""
    base_style = (
        "Style: cinematic, elegant, minimal. Gold color is warm amber (#D4A843). "
        "Font style resembles Trajan Pro or Cinzel — bold, serif, biblical weight. "
        "Subtle golden light particles floating in the background. "
        "No people, no objects — text only on black."
    )

    text = card["text"]
    card_type = card["type"]

    if card_type == "scripture":
        return (
            f'A 1920x1080 scripture card with pure black background. '
            f'Centered gold serif text with subtle outer glow that reads exactly:\n\n'
            f'{text}\n\n{base_style}'
        )
    elif card_type == "question":
        return (
            f'A 1920x1080 card with pure black background. '
            f'Large centered gold serif text with subtle outer glow that reads exactly: '
            f'"{text}" '
            f'Dramatic, minimal, cinematic. {base_style}'
        )
    elif card_type == "title":
        return (
            f'A 1920x1080 title card with pure black background. '
            f'Large centered gold serif text with dramatic outer glow that reads exactly:\n\n'
            f'{text}\n\n'
            f'Epic, cinematic title card feel. {base_style}'
        )
    elif card_type == "byword":
        return (
            f'A 1920x1080 card with pure black background. '
            f'Large centered WHITE bold serif text that reads exactly: "{text}" '
            f'Stark, cold, impactful. No gold — white text on black. '
            f'Minimal golden particles in background. No people, no objects.'
        )
    elif card_type == "byword_final":
        return (
            f'A 1920x1080 card with pure black background. '
            f'Very large centered GOLD bold serif text with strong outer glow that reads exactly: '
            f'"{text}" '
            f'This is the reveal — bigger and brighter than previous cards. {base_style}'
        )
    elif card_type == "emphasis":
        return (
            f'A 1920x1080 card with pure black background. '
            f'Very large centered gold bold serif text with pulsing outer glow that reads exactly: '
            f'"{text}" '
            f'Dramatic, powerful, heavy weight. {base_style}'
        )
    elif card_type == "verdict":
        return (
            f'A 1920x1080 card with pure black background. '
            f'Centered gold serif text with subtle outer glow that reads exactly: '
            f'"{text}" '
            f'The checkmark should be bright gold. Clean, verdict-style. {base_style}'
        )
    elif card_type == "logo":
        return (
            f'A 1920x1080 channel logo card with pure black background. '
            f'Large centered gold serif text with divine outer glow that reads exactly: '
            f'"{text}" '
            f'Below the text, a subtle golden subscribe button icon. {base_style}'
        )
    else:
        return f'A 1920x1080 card with pure black background. Gold serif text: "{text}". {base_style}'


def generate_card(client, card, model="dall-e-3"):
    """Generate a single card image and save it."""
    card_id = card["id"]
    filename = OUTPUT_DIR / f"card-{card_id:02d}-{card['type']}.png"

    if filename.exists():
        print(f"  ⏭️  Card {card_id} already exists, skipping")
        return filename

    prompt = build_prompt(card)
    print(f"  🎨 Generating card {card_id}: {card['text'][:50]}...")

    try:
        response = client.images.generate(
            model=model,
            prompt=prompt,
            n=1,
            size="1792x1024",  # Closest to 1920x1080 that DALL-E supports
            quality="hd",
        )

        image_url = response.data[0].url
        image_data = requests.get(image_url).content

        with open(filename, "wb") as f:
            f.write(image_data)

        print(f"  ✅ Saved: {filename.name}")
        return filename

    except Exception as e:
        print(f"  ❌ Card {card_id} failed: {e}")
        return None


def main():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ Set your OpenAI API key first:")
        print("   set OPENAI_API_KEY=sk-your-key-here")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    # Check for single card mode
    single_card = None
    if "--card" in sys.argv:
        idx = sys.argv.index("--card")
        if idx + 1 < len(sys.argv):
            single_card = int(sys.argv[idx + 1])

    if single_card:
        card = next((c for c in CARDS if c["id"] == single_card), None)
        if not card:
            print(f"❌ Card {single_card} not found")
            sys.exit(1)
        print(f"\n🎬 Generating single card #{single_card}")
        generate_card(client, card)
    else:
        print(f"\n🎬 DEUTERONOMY 28 — SCRIPTURE CARD GENERATOR")
        print(f"   Generating {len(CARDS)} cards to {OUTPUT_DIR}\n")

        success = 0
        failed = 0

        for card in CARDS:
            result = generate_card(client, card)
            if result:
                success += 1
            else:
                failed += 1
            # Rate limit — DALL-E allows ~7 images/min on most tiers
            time.sleep(10)

        print(f"\n{'='*50}")
        print(f"✅ Generated: {success}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Output: {OUTPUT_DIR}")
        print(f"\nNext: Import all PNGs into CapCut timeline")


if __name__ == "__main__":
    main()
