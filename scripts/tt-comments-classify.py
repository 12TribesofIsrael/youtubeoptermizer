"""
Parse TT comments scraped via browser_pilot.py, classify each by intent,
and pair with a reply template. Output: output/tt-comments-to-reply.md
"""
import json
import re
import sys
from pathlib import Path

LOG = Path("analytics/_tt-scrape-v4.log")
VIDEO_ID = "7629867741511486734"
VIDEO_URL = f"https://www.tiktok.com/@aibiblegospels_/video/{VIDEO_ID}"
OUT = Path("output/tt-comments-to-reply.md")

REPLY_TEMPLATES = {
    "identity": [
        "Shalom 🙌🏿 we break this down tribe-by-tribe in the Telegram — t.me/aibiblegospels — free, drops daily",
        "That's the question Deut 28 answers 📖 full breakdown is pinned in t.me/aibiblegospels — join the family",
        "The signs are in your bloodline 🔱 we map all 12 tribes weekly in the Telegram — link in bio",
        "ALL PRAISES — that's exactly why I made the Telegram. Tribe-by-tribe drops. Link in bio 🙏🏿",
        "Family, the answer is in the curses + blessings 📜 deeper breakdown daily → t.me/aibiblegospels",
    ],
    "intent": [
        "Link's in bio 👆🏿 — t.me/aibiblegospels — daily drops, all free",
        "Telegram has the full series — t.me/aibiblegospels — pinned in bio",
        "Tap the bio link 🔱 we drop a new piece every day in there",
        "YouTube has the 80+ episode series — handle's in bio. Telegram for daily breakdowns",
        "Pulled up. Bio link → Telegram → daily prophecy decoded 📖",
    ],
    "affirmer": [
        "Shalom family 🙌🏿",
        "ALL PRAISES TO THE MOST HIGH 🔱",
        "We see you fam 🙏🏿",
        "Tribe checking in ✊🏿",
        "Stay rooted 📜",
    ],
    "skeptic": [
        "Read Deut 28:15-68 slow — every curse, then look at the diaspora. Decide for yourself 📖",
        "The receipts are in scripture, not in me. Deut 28, Joel 3, Isaiah 11 — that's the homework 🔱",
        "Appreciate the engagement 🙏🏿 — but the test is the Word, not the messenger. Read the chapter",
        "Faith ain't a feeling, it's a study. Pull Deut 28 up and walk through it with me",
        "I'm not asking you to believe me. I'm asking you to read your Bible 📜",
    ],
    "faithwalk": [
        "Min. Zay's walking from Philly → Cali, 633+ miles in 🌎 live tracker at faithwalklive.com",
        "Real minister, real walk. Live map at faithwalklive.com — tap 'Updates'",
        "That's Faith Walk Live — Day 33+ on the road. Real-time tracker → faithwalklive.com",
    ],
    "tribe_claim": [
        "🔱 We see you family. Confirm in the Telegram — t.me/aibiblegospels — we map each tribe weekly",
        "ALL PRAISES 🙌🏿 — tribe-by-tribe breakdown drops daily in the Telegram. Link in bio",
        "Shalom 📜 — Levi/Judah/Benjamin breakdowns + more in t.me/aibiblegospels",
    ],
    "scripture_quoter": [
        "📖 The Word never returns void. Pinned breakdown of that passage in t.me/aibiblegospels",
        "🔱 ALL PRAISES — that's the receipt. Daily verse-by-verse in the Telegram",
        "Scripture-grounded family 🙏🏿 we go deeper daily → t.me/aibiblegospels",
    ],
    "hate": [],  # ignore
}

# Classification heuristics — keyword-based, ordered by priority
def classify(text: str) -> str:
    t = text.lower()

    # Hateful / dismissive first (skip if so)
    hate_kw = ["fake", " cap", "stop lying", "this is bs", "bullshit", "demonic", "heresy", "false prophet", "blasphemy"]
    if any(k in t for k in hate_kw):
        return "hate"

    # Faith Walk reference
    if any(k in t for k in ["faith walk", "faithwalk", "minister zay", "min zay", "min. zay", "the walk", "walking to cali"]):
        return "faithwalk"

    # Skeptic — questioning the message itself OR a substantive critique
    skeptic_kw = [" ai ", "ai voice", "ai generated", "not real", "not true", "where's your source", "where is your source",
                  "where's the proof", "where is the proof", "prove it", "wrong", "incorrect", "not biblical",
                  "made up", "deceiving", "white man's voice", "white mans voice", "white voice", "who is really",
                  "who really benefits", "who really making"]
    if any(k in t for k in skeptic_kw):
        return "skeptic"

    # Intent-buyer — directly asking how to learn more
    intent_kw = ["where can i", "where do i", "how do i learn", "more info", "tell me more", "drop the link",
                 "what's the link", "share the link", "send the link", "follow you", "where's the rest"]
    if any(k in t for k in intent_kw):
        return "intent"

    # Identity-curious — "what tribe am I", lineage questions
    identity_kw = ["what tribe", "which tribe", "my tribe", "am i a", "am i from", "i'm from", "i am from",
                   "lost tribe", "lost tribes", "where do i come from", "my lineage", "my ancestry",
                   "am i an israelite", "are we", "who am i", "son of jacob", "son of john"]
    if any(k in t for k in identity_kw):
        return "identity"

    # Tribe claim — naming their tribe (frequent in this audience)
    tribe_kw = ["judah", "levi", "benjamin", "binyamyan", "manasseh", "manashah", "ephraim", "apharayam",
                "naphtali", "naphataly", "reuben", "ra'uban", "ruben", "dan ", "gad ", "asher", "ashar",
                "issachar", "yashakar", "zebulun", "zabalawan", "simeon", "sham'wan", "haiti", "ayiti",
                "jamaican", "puerto rican", "cuban", "dominican", "bahamas", "trinidad",
                "i'm a ", "i am a "]
    if any(k in t for k in tribe_kw):
        return "tribe_claim"

    # Scripture-quoter — they quote a verse or reference one
    scripture_kw = ["deuteronomy", "deut ", "joel", "isaiah", "psalm", "matthew", "revelation", "genesis",
                    "exodus", "ezekiel", "jeremiah", "yashua", "yahweh", "yhwh", "elohim", "torah",
                    "chapter", "verse", "scripture says"]
    if any(k in t for k in scripture_kw):
        return "scripture_quoter"

    # Affirmer — short praise/emoji
    affirm_short = ["shalom", "amen", "praise", "all praises", "thank you", "thank god", "blessed",
                    "🙌", "🙏", "🔱", "💪", "🔥", "✊", "facts", "truth", "preach", "yes"]
    if any(k in t for k in affirm_short) or len(text.strip()) < 30:
        return "affirmer"

    # Default: treat as affirmer (low-effort comment, heart-only)
    return "affirmer"


def parse_log(log_path: Path) -> list[dict]:
    """Extract concatenated payload from sliced Result: lines."""
    text = log_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    # Find "built X items, payload=Y bytes" line — slices come after it
    start_idx = None
    for i, line in enumerate(lines):
        if "built" in line and "payload=" in line:
            start_idx = i + 1
            break
    if start_idx is None:
        raise RuntimeError("Couldn't find 'built X items, payload=Y' marker in log")

    # Each slice line: '  Result: "<JSON chunk with escapes>"'
    pattern = re.compile(r'^\s+Result:\s+"(.*)"\s*$')
    chunks = []
    for line in lines[start_idx:]:
        m = pattern.match(line)
        if not m:
            continue
        raw = m.group(1)
        if raw == "missing":
            break
        # Unescape JSON string literal escapes that browser_pilot embedded
        try:
            chunk = json.loads(f'"{raw}"')
        except json.JSONDecodeError:
            chunk = raw
        chunks.append(chunk)

    payload = "".join(chunks)
    if not payload:
        raise RuntimeError("No payload chunks recovered")

    return json.loads(payload)


def main():
    items = parse_log(LOG)
    print(f"Parsed {len(items)} comments from log", file=sys.stderr)

    # Classify + assign template
    classified = []
    OWN_HANDLE = "aibiblegospels_"
    for item in items:
        handle = item.get("h", "")
        display = item.get("d", "")
        likes = item.get("l", 0)
        comment = item.get("c", "").strip()
        # Skip own replies
        if handle == OWN_HANDLE:
            continue
        # Skip rows where "comment" is just the display name echoing back
        if not comment or comment.lower() == display.strip().lower():
            continue
        # Skip "· Friend" / "· Creator" pseudo-tags
        if comment.startswith("·") or comment in ("Friend", "Creator"):
            continue
        bucket = classify(comment)
        templates = REPLY_TEMPLATES.get(bucket, [])
        # Pick a template — rotate by handle hash for variety
        suggested = templates[hash(handle) % len(templates)] if templates else "(ignore — don't reply)"
        classified.append({
            "handle": handle,
            "likes": likes,
            "comment": comment,
            "bucket": bucket,
            "reply": suggested,
        })

    # Sort: reply-worthy buckets first, then by likes desc
    priority = {"identity": 0, "intent": 1, "tribe_claim": 2, "skeptic": 3, "faithwalk": 4,
                "scripture_quoter": 5, "affirmer": 6, "hate": 99}
    classified.sort(key=lambda x: (priority.get(x["bucket"], 50), -x["likes"]))

    # Bucket counts
    counts = {}
    for c in classified:
        counts[c["bucket"]] = counts.get(c["bucket"], 0) + 1

    # Write markdown
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        f.write("# TikTok comment reply queue\n\n")
        f.write(f"**Source:** [viral post]({VIDEO_URL}) — {len(items)} comments scraped\n\n")
        f.write("**Counts by bucket:**\n\n")
        for b in sorted(counts, key=lambda b: priority.get(b, 50)):
            n = counts[b]
            note = "✅ reply" if b not in ("hate",) else "❌ ignore"
            f.write(f"- **{b}** ({n}) — {note}\n")
        f.write("\n---\n\n")
        f.write("## How to use\n\n")
        f.write("1. Open the [viral post]({}) in your browser\n".format(VIDEO_URL))
        f.write("2. For each row below, find the commenter, paste the suggested reply\n")
        f.write("3. For **affirmers** — just heart, no reply needed unless their comment has 3+ likes\n")
        f.write("4. For **hate** — skip\n\n")
        f.write("---\n\n")

        for row in classified:
            if row["bucket"] == "hate":
                continue
            handle_url = f"https://www.tiktok.com/@{row['handle']}"
            f.write(f"### @{row['handle']} — `{row['bucket']}` — {row['likes']} likes\n\n")
            f.write(f"**Their comment:**\n> {row['comment']}\n\n")
            f.write(f"**Suggested reply:**\n```\n{row['reply']}\n```\n\n")
            f.write(f"[Open profile]({handle_url})\n\n---\n\n")

    print(f"Wrote {OUT}", file=sys.stderr)
    print(f"Total comments: {len(items)} | Reply-worthy: {sum(1 for c in classified if c['bucket'] != 'hate')}", file=sys.stderr)


if __name__ == "__main__":
    main()
