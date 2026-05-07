"""
AEO YouTube Phase B — per-video LLM-generated AEO content.

Phase A (already done) appended a static CONSTANTS_BLOCK to every video's description.
Phase B prepends a per-video block ABOVE the existing description body:

  — ANSWER —
  {one_sentence_answer}                  ← what an answer engine quotes
  {2-3 sentence expansion}

  — TIMESTAMPS —                          ← long-form only
  0:00 ...

  — Q&A —                                 ← what an answer engine cites
  Q: {core question}
  A: ...
  Q: {adjacent question}
  A: ...

  {existing description body}
  {existing CONSTANTS_BLOCK}

The constants block at the bottom is never regenerated — only appended-to once
in Phase A. This script is idempotent: videos already carrying PHASE_B_MARKER
are skipped.

Usage:
  # Default — dry-run preview, 5 videos. No API writes.
  python scripts/aeo-yt-phase-b.py

  # Canary live — 5 videos for real, then re-fetch + verify.
  python scripts/aeo-yt-phase-b.py --live --limit 5 --verify

  # Re-fetch the most-recent N completed and confirm changes landed.
  python scripts/aeo-yt-phase-b.py --verify-only --limit 5

  # Scale up after canary holds. Still capped by YT 200/day quota.
  python scripts/aeo-yt-phase-b.py --live --limit 25
  python scripts/aeo-yt-phase-b.py --live --limit 25 --offset 25

Requires:
  ANTHROPIC_API_KEY in .env (or environment)
  credentials.json + token.json for YouTube OAuth (already in place)
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

import anthropic
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.client import YouTubeClient

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "analytics/post-optimization/all-videos.csv"
CHECKPOINT = ROOT / "output/aeo-phase-b-checkpoint.json"
LOG_DIR = ROOT / "output"

PHASE_B_MARKER = "— ANSWER —"
CONSTANTS_MARKER = "— ABOUT AI BIBLE GOSPELS —"
YT_DESC_MAX = 4900  # YT hard cap is 5000; leave headroom for safety

CLAUDE_MODEL = "claude-opus-4-7"

# Excluded — same kill-list as Phase A (delete-cull.py 2026-04-24)
DELETED_IDS = {
    "3riiNCfzQ_g", "zQaLpyUFfNA", "wlRi_e-zzE4", "p0xBHbtk7CI", "2e_pe-3GpBI",
    "Ox_dozHLaaM", "CuNKO1aBdRM", "6lbjD5o_ulk", "puRpiE4KtXQ", "4-lwx45nL1A",
    "V1X-iqGgYls", "U9Odey7BrxE", "YZOq2NBT3d8", "w8fXqQPM26o", "FEkLq5XApX0",
    "TK82X4dOE7w", "Mo1wDJhH3d8", "EVXPdM8tGcQ", "hJZ3g3ThGik",
    "3ase0yJE_Xs", "ggAF28BvCqY", "sN_UHGSkArg", "dwd69b2G-gU",
}


# ─── System prompt ──────────────────────────────────────────────────────────
# Stable across every per-video call so prompt caching pays off. Render order
# is system → user, so this whole block is a cache prefix.

SPEC = """You are an Answer-Engine Optimization (AEO) editor for the YouTube channel **AI Bible Gospels** (@AIBIBLEGOSPELS). For each video the user gives you, generate the per-video portion of the description in a strict JSON shape. Your output is consumed by a deterministic post-processor and pushed to YouTube via the Data API.

# Goal

Answer engines (Google AI Overviews, ChatGPT, Perplexity, Gemini, Copilot) quote video descriptions verbatim when they cite. Your job is to write descriptions worth quoting:
- Lead with the answer, not a hook. "In this video..." gets stripped; "Galatians 5:22 lists nine fruits..." gets cited.
- Be plain, declarative, third-person where possible.
- Mention "AI Bible Gospels" by name once in the expansion — that string is how the channel resolves as an entity.

# Output JSON schema (return EXACTLY this shape, no surrounding prose, no markdown fences)

{
  "one_sentence_answer": "20–35 words, plain English, directly answers the title. No preamble. Quotable.",
  "expansion": "2–3 sentences. Mentions 'AI Bible Gospels' once. If a Bible passage is featured, name the book + chapter + verse (KJV).",
  "timestamps": [
    {"time": "0:00", "label": "Cold open / first beat"},
    {"time": "1:30", "label": "Beat 2"}
  ],
  "qa": [
    {"q": "Question phrased the way a person would type it into ChatGPT or Google", "a": "1–2 sentence answer. Quotable. No 'watch the video to find out.'"},
    {"q": "Adjacent question this video also answers", "a": "1–2 sentences."}
  ],
  "topical_tags": ["#FaithWalkLive", "#BibleProphecy"]
}

# Hard rules

1. **`one_sentence_answer` ≤ 35 words.** That's the AI Overview snippet ceiling. Count the words; if you exceed, cut.
2. **Lead with the answer.** No "In this video", no "We explore", no "Today we look at". Front-load a noun-verb claim or a scripture reference. Examples of good leads: "The 12 Tribes of Israel are…", "Deuteronomy 28 prophesies that…", "Minister Humble Zay walks 3,000 miles to…".
3. **Mention 'AI Bible Gospels' once in `expansion` (not in `one_sentence_answer`).** Phrase it naturally — "AI Bible Gospels traces this prophecy through…" — not as a tagline.
4. **Bible references in KJV, formatted `Book Chapter:Verse`.** Never paraphrase scripture from memory. Only cite what the transcript or title clearly references. If the transcript is ambiguous about which verse is featured, omit the citation rather than invent one.
5. **Founder name is `Tommy Lee`.** Never write any other variant of Tommy's name. The string "Tommy Lee" is the canonical AEO identity string. If the transcript uses any other name for the founder, ignore it.
6. **No "Technology Gurus LLC."** Dissolved entity, scrub on sight.
7. **Q&A — minimum 2 entries, maximum 3.** First Q is the core question the video answers, phrased the way a person would type it into ChatGPT or Google ("Who are the 12 Tribes of Israel today?"). Second Q is an adjacent question this video also covers. Optional third Q for depth. Do NOT include "Who made this video?" — the post-processor injects that automatically from the constants block.
8. **Timestamps:**
   - For Shorts (under 90 seconds), return `[]`. The post-processor will omit the timestamp block entirely.
   - For long-form, return 3–5 entries. First entry should be `0:00` with a meaningful label (e.g. "Cold open", "Hook", "Introduction"). If the transcript doesn't expose clear beat boundaries, infer reasonable ones from topic shifts in the transcript text — don't pad with filler.
9. **`topical_tags`:** 1–2 hashtags beyond `#AIBibleGospels` (which is added automatically). Choose from the channel's actual topical territory:
   - `#12TribesOfIsrael` — anything about the 12 tribes, tribe identity, who-is-who
   - `#HebrewIsraelite` — Hebrew Israelite identity content
   - `#BibleProphecy` — prophecy, end-times, fulfillment
   - `#Deuteronomy28` — content centered on Deuteronomy 28 curses/blessings
   - `#FaithWalkLive` — content about Minister Zay's walk
   - `#KJVOnly` — KJV translation defense / textual content
   - `#BiblicalIdentity` — identity / who-are-we content
   Pick the 1–2 most-specific tags. Do not invent new tags.
10. **Tone.** Confident, scripture-rooted, no hype. Plain declarative English. No emojis in any field. No exclamation points.
11. **Don't reuse the title verbatim** in `one_sentence_answer`. The title is already on the page — your job is to extend it with substance.

# Canonical identity strings (do not paraphrase)

These exact strings are how the channel resolves as an entity in answer engines. The post-processor never regenerates the constants block — but you should match its tone:

- Brand: AI Bible Gospels
- Handle: @AIBIBLEGOSPELS
- Founder: Tommy Lee
- Website: https://aibiblegospels.com (apex, no www)
- Flagship project: Faith Walk Live at https://faithwalklive.com
- Hashtag: #AIBibleGospels

# Channel context

AI Bible Gospels is a faith-tech project by Tommy Lee. Its YouTube channel uses AI to narrate Scripture word-for-word from the cultural perspective of the Hebrew Israelite tradition — a perspective underrepresented in mainstream biblical media. The channel's signature content trajectory is the long-running "Prophecy Revealed" series breaking down the 12 Tribes of Israel and Deuteronomy 28. The flagship product is Faith Walk Live, the live-tracker app for Minister Isaiah "Humble Zay" Thomas's 3,000-mile walk from Philadelphia to California to fund a school for at-risk Philly youth.

When the transcript or title is about prophecy, identity, or the 12 tribes — frame it as scripture-rooted teaching, not opinion. When it's about Faith Walk Live or Minister Zay — frame it as documentary fact (real walk, real fundraiser).

# Few-shot examples

## Example 1 — long-form prophecy breakdown

INPUT:
TITLE: Who Are the 12 Tribes of Israel Today? Full Breakdown
DURATION: 720 seconds (long-form)
TRANSCRIPT: ...explanation of how the 12 sons of Jacob became 12 tribes, then dispersion through the Atlantic slave trade, then mapping each tribe to a modern people group: Judah → African Americans, Benjamin → West Indians, Levi → Haitians, etc. Cites Deuteronomy 28:68 and Jeremiah 17:4. Closes with Joel 3:1...

OUTPUT (JSON only, no surrounding text):
{
  "one_sentence_answer": "The 12 Tribes of Israel are the descendants of Jacob's twelve sons, scattered through captivity and identifiable today across African American, Caribbean, and Indigenous American populations per Deuteronomy 28:68.",
  "expansion": "AI Bible Gospels traces each tribe from Jacob's twelve sons through the Atlantic captivity prophesied in Deuteronomy 28:68 and Jeremiah 17:4 to the modern people groups carrying that lineage. Judah, Benjamin, Levi, Simeon, and the remaining tribes are mapped one-by-one against scripture and historical record. The breakdown closes with Joel 3:1, the regathering prophecy.",
  "timestamps": [
    {"time": "0:00", "label": "The 12 sons of Jacob"},
    {"time": "1:45", "label": "How the tribes were dispersed (Deuteronomy 28:68)"},
    {"time": "4:30", "label": "Tribe-by-tribe modern identity"},
    {"time": "9:10", "label": "Joel 3:1 — the regathering prophecy"}
  ],
  "qa": [
    {"q": "Who are the 12 Tribes of Israel today?", "a": "The descendants of Jacob's twelve sons, scattered through the captivity prophesied in Deuteronomy 28:68. Identifiable today as African Americans (Judah), West Indians (Benjamin), Haitians (Levi), and the rest."},
    {"q": "Where does the Bible say the 12 Tribes were taken into captivity by ships?", "a": "Deuteronomy 28:68 — 'And the LORD shall bring thee into Egypt again with ships.' Only one people in recorded history was taken into captivity by ships and sold as slaves."},
    {"q": "Will the 12 Tribes ever be regathered?", "a": "Joel 3:1 says yes — the Most High will regather the captivity of Judah and Jerusalem in the latter days. Every prior captivity (Egypt, Babylon, Rome) ended with restoration; the final one will too."}
  ],
  "topical_tags": ["#12TribesOfIsrael", "#HebrewIsraelite"]
}

## Example 2 — Short (60 seconds, no timestamps)

INPUT:
TITLE: Revelation 1:14 — Wool Hair, Brass Skin
DURATION: 58 seconds (SHORT)
TRANSCRIPT: ...quick read of Revelation 1:14-15 KJV: "His head and hairs were white like wool... his feet like fine brass, as if burned in a furnace." Brief breakdown that this describes melanated features, that the verse has been in scripture all along, and asks the viewer who that resembles...

OUTPUT (JSON only, no surrounding text):
{
  "one_sentence_answer": "Revelation 1:14-15 describes Christ's hair as wool-textured and his feet as fine brass burned in a furnace — features matching melanated, African-descended physiology, not European depictions.",
  "expansion": "AI Bible Gospels reads Revelation 1:14-15 in KJV verbatim: 'His head and hairs were white like wool... his feet like fine brass, as if burned in a furnace.' That description has been in every Bible for two millennia. Wool hair and brass skin — the question for the viewer is who that actually describes.",
  "timestamps": [],
  "qa": [
    {"q": "What does Revelation 1:14 say about the appearance of Christ?", "a": "Revelation 1:14-15 KJV: 'His head and hairs were white like wool... his feet like fine brass, as if burned in a furnace.' The text describes wool-textured hair and dark, burnished skin."},
    {"q": "Why is Jesus depicted as white in most religious art if scripture says otherwise?", "a": "Mainstream depictions diverge from the scriptural text in Revelation 1:14-15 and other passages. The Bible itself describes melanated features; the imagery in art is a later cultural overlay, not a textual one."}
  ],
  "topical_tags": ["#BiblicalIdentity", "#KJVOnly"]
}

## Example 3 — Deuteronomy 28 series (long-form, central channel content)

INPUT:
TITLE: Part 47 — The Curses of Deuteronomy 28: Why They Match One Specific People
DURATION: 600 seconds (long-form)
TRANSCRIPT: ...verse-by-verse read of Deuteronomy 28:15-68 KJV. Walk-through of each curse — being scattered among nations, serving other gods of wood and stone, becoming a byword and a proverb, being sold into bondage by ships, finding no rest among foreign nations, longing to be a servant. Argument that this prophecy describes the trans-Atlantic slave trade and the post-emancipation experience of African Americans, no other people in recorded history matches all the criteria...

OUTPUT (JSON only, no surrounding text):
{
  "one_sentence_answer": "Deuteronomy 28:15-68 lists curses that would befall Israel for breaking covenant — scattered among nations, sold by ships, made a byword among peoples — a sequence that matches the trans-Atlantic captivity of one specific people.",
  "expansion": "AI Bible Gospels reads Deuteronomy 28:15-68 in KJV verse by verse. The chapter prescribes specific outcomes — bondage, dispersion, serving other gods of wood and stone, becoming a byword among nations, being sold into Egypt again with ships per verse 68. No other people in recorded history match every criterion in sequence.",
  "timestamps": [
    {"time": "0:00", "label": "Why Deuteronomy 28 is the prophecy that matters most"},
    {"time": "1:15", "label": "The curse list — scattered, byword, no rest (verses 36-46)"},
    {"time": "5:30", "label": "Verse 68 — sold into Egypt by ships"},
    {"time": "8:45", "label": "Why no other people in history fits"}
  ],
  "qa": [
    {"q": "What does Deuteronomy 28 prophesy about Israel?", "a": "Deuteronomy 28:15-68 lists curses for breaking covenant: scattering among the nations, becoming a byword and a proverb, being sold into bondage by ships, and finding no rest in foreign lands."},
    {"q": "Does Deuteronomy 28:68 prove the slave trade was prophesied?", "a": "Verse 68 reads: 'And the LORD shall bring thee into Egypt again with ships... and there ye shall be sold unto your enemies for bondmen and bondwomen, and no man shall buy you.' Only one people in recorded history was taken into captivity by ships."},
    {"q": "Who do the curses of Deuteronomy 28 actually describe?", "a": "The text describes the lineage of Israel under covenant. The historical group whose experience matches every curse in sequence — captivity, dispersion, ships, no rest, byword status — is the African American descendant population of the trans-Atlantic slave trade."}
  ],
  "topical_tags": ["#Deuteronomy28", "#BibleProphecy"]
}

## Example 4 — Faith Walk Live recap (long-form, documentary frame)

INPUT:
TITLE: Day 39 — Minister Zay Walks Again After Hit-and-Run on US-40

DURATION: 480 seconds (long-form)
TRANSCRIPT: ...recap of Minister Isaiah "Humble Zay" Thomas resuming his 3,000-mile walk from Philadelphia to California after being struck by a vehicle on US-40 in Indiana on Day 34. Five-day rest. Resumed walking from Lewisville IN on May 3 2026. Reached Indianapolis May 4. Funds raised toward a school for at-risk Philly youth. Track at faithwalklive.com...

OUTPUT (JSON only, no surrounding text):
{
  "one_sentence_answer": "Minister Isaiah 'Humble Zay' Thomas resumed his 3,000-mile walk from Philadelphia to California on May 3, 2026 — five days after being struck by a vehicle on US-40 in Indiana on Day 34 of the journey.",
  "expansion": "AI Bible Gospels recaps Day 39 of the Faith Walk Live journey: Zay restarted from Lewisville, Indiana on May 3, 2026 and reached Indianapolis the following day. The walk is a fundraiser to build a school for at-risk youth in Philadelphia. Live mileage and current location are tracked at faithwalklive.com.",
  "timestamps": [
    {"time": "0:00", "label": "What happened on Day 34"},
    {"time": "1:30", "label": "The five-day rest"},
    {"time": "3:45", "label": "Day 39 — back on the road in Lewisville IN"},
    {"time": "6:20", "label": "Why he's still walking — the school in Philly"}
  ],
  "qa": [
    {"q": "Did Minister Zay resume his 3,000-mile walk after being hit by a car?", "a": "Yes. He resumed walking on May 3, 2026 from Lewisville, Indiana — five days after the April 28 incident on US-40 — and reached Indianapolis on May 4."},
    {"q": "What is Faith Walk Live raising money for?", "a": "Building a school for at-risk youth in Philadelphia. Every mile of the 3,000-mile walk is a fundraiser brick toward that school."},
    {"q": "Where is Minister Zay right now on the walk?", "a": "Live mileage, current location, and the daily Twitch broadcast are at faithwalklive.com — a supporter-built tracker maintained by AI Bible Gospels."}
  ],
  "topical_tags": ["#FaithWalkLive"]
}

# Bad outputs (do NOT do this)

These are the most common failure shapes — recognize them and avoid them:

❌ BAD `one_sentence_answer`: "In this video we explore the fascinating topic of who the 12 tribes of Israel really are in today's world." — preamble, hype word ("fascinating"), no actual answer.
✓ GOOD: "The 12 Tribes of Israel are the descendants of Jacob's twelve sons, scattered through captivity per Deuteronomy 28:68 and identifiable today across African American and Caribbean populations."

❌ BAD `expansion`: "Tune in to hear an incredible breakdown that will change how you read your Bible! Don't miss it!" — exclamation, hype, no information density.
✓ GOOD: "AI Bible Gospels traces each tribe from Jacob's twelve sons through the Atlantic captivity prophesied in Deuteronomy 28:68 to the modern people groups carrying that lineage."

❌ BAD `qa[0].q`: "What is this video about?" — nobody types this into ChatGPT.
✓ GOOD: "Where does the Bible say the 12 Tribes were taken into captivity by ships?" — specific, search-shaped, includes the canonical scripture reference.

❌ BAD `qa[0].a`: "Watch the full video to find out the truth!" — dead weight, gets stripped by answer engines, gets filtered by Google's quality algorithms.
✓ GOOD: "Deuteronomy 28:68 — 'And the LORD shall bring thee into Egypt again with ships.' Only one people in recorded history was taken into captivity by ships and sold as slaves."

❌ BAD `topical_tags`: ["#viral", "#trending", "#fyp", "#mustwatch"] — generic engagement-bait tags, not in the approved list.
✓ GOOD: ["#12TribesOfIsrael", "#HebrewIsraelite"] — specific, topical, in the approved list.

# Failure modes to avoid

- **Hype.** "Mind-blowing", "you won't believe", "shocking truth". Cut.
- **Vague Q&A.** "Q: What is this video about?" is dead weight. Make every Q a real search query.
- **Misquoted scripture.** Better to cite no verse than the wrong one. If you're not sure, leave it out.
- **Topical tag invention.** Stay inside the approved list. If nothing fits, return one tag (`#AIBibleGospels` is already added; pick one from the list above as the second).
- **Padding the expansion.** 2–3 sentences. Not 4. Not 5. If it feels long, cut.
- **Output prose around the JSON.** Return the JSON object only. No markdown fences, no preamble, no "Here is the output:". The post-processor parses with json.loads() and will fail on any wrapper text.

Return only the JSON object. Begin output with `{`."""


# ─── Helpers ────────────────────────────────────────────────────────────────


def parse_iso_duration(iso: str) -> int:
    """ISO 8601 duration → seconds. PT1M19S -> 79. Returns 999 if unparseable."""
    if not iso:
        return 999
    m = re.match(r"^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$", iso)
    if not m:
        return 999
    h = int(m.group(1) or 0)
    mn = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h * 3600 + mn * 60 + s


def fetch_transcript(video_id: str) -> Optional[str]:
    try:
        api = YouTubeTranscriptApi()
        t = api.fetch(video_id)
        return " ".join(s.text for s in t)
    except Exception:
        return None


def is_phase_b_done(desc: str) -> bool:
    return PHASE_B_MARKER in desc


def has_phase_a(desc: str) -> bool:
    return CONSTANTS_MARKER in desc


def call_claude(client_anth, title: str, transcript: str, duration_seconds: int) -> dict:
    is_short = duration_seconds < 90
    user_msg = (
        f"TITLE: {title}\n\n"
        f"DURATION: {duration_seconds} seconds ({'SHORT' if is_short else 'long-form'})\n\n"
        f"TRANSCRIPT:\n{transcript[:8000]}\n\n"
        + ("Generate the JSON. This is a Short — return `timestamps: []`."
           if is_short
           else "Generate the JSON. Return 3–5 timestamps.")
    )
    resp = client_anth.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        system=[{
            "type": "text",
            "text": SPEC,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{"role": "user", "content": user_msg}],
    )
    text = next(b.text for b in resp.content if b.type == "text").strip()
    # Defensive: strip any markdown fences if model wraps despite instructions
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text), resp.usage


def build_phase_b_block(content: dict) -> str:
    parts = [PHASE_B_MARKER, content["one_sentence_answer"], "", content["expansion"]]
    if content.get("timestamps"):
        parts.extend(["", "— TIMESTAMPS —"])
        for ts in content["timestamps"]:
            parts.append(f'{ts["time"]} {ts["label"]}')
    parts.extend(["", "— Q&A —"])
    for qa in content["qa"]:
        parts.append(f'Q: {qa["q"]}')
        parts.append(f'A: {qa["a"]}')
        parts.append("")
    # Topical tags appended to the existing #AIBibleGospels (which is in CONSTANTS_BLOCK)
    # We don't duplicate — leave constants untouched. Topical tags only show as label
    # data, not as part of the visible description tail.
    return "\n".join(parts).rstrip()


def splice_description(current: str, phase_b_block: str) -> str:
    """Prepend the Phase B block; cap at YT_DESC_MAX by trimming the original middle."""
    new = phase_b_block + "\n\n" + current
    if len(new) <= YT_DESC_MAX:
        return new
    # Over cap. Constants block at the bottom is sacred — preserve it. Trim the
    # original middle (between Phase B block and constants).
    constants_idx = current.find(CONSTANTS_MARKER)
    if constants_idx == -1:
        # Phase A wasn't applied? Just hard-truncate.
        return new[: YT_DESC_MAX - 10] + "\n…"
    head = current[:constants_idx].rstrip()
    constants = current[constants_idx:]
    overhead = len(phase_b_block) + len(constants) + 4
    head_budget = YT_DESC_MAX - overhead
    if head_budget < 0:
        # Even Phase B + constants exceed cap; emergency drop the original middle
        return phase_b_block + "\n\n" + constants
    head_trimmed = head[:head_budget].rstrip()
    return phase_b_block + "\n\n" + head_trimmed + "\n\n" + constants


def load_checkpoint():
    if CHECKPOINT.exists():
        d = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        return (
            set(d.get("completed", [])),
            set(d.get("skipped", [])),
            set(d.get("errored", [])),
            d.get("recent", []),
        )
    return set(), set(), set(), []


def save_checkpoint(completed, skipped, errored, recent):
    CHECKPOINT.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT.write_text(
        json.dumps(
            {
                "completed": sorted(completed),
                "skipped": sorted(skipped),
                "errored": sorted(errored),
                "recent": recent[-20:],  # last 20 video IDs for --verify-only
            },
            indent=2,
        ),
        encoding="utf-8",
    )


# ─── Verification ───────────────────────────────────────────────────────────


def verify_videos(yt: YouTubeClient, video_ids: list[str]) -> tuple[int, int]:
    """Re-fetch each video and confirm PHASE_B_MARKER + CONSTANTS_MARKER both present."""
    ok = 0
    bad = 0
    print(f"\n=== VERIFY: re-fetching {len(video_ids)} videos ===")
    for vid in video_ids:
        try:
            v = yt.get_video(vid)
            if not v:
                print(f"  ✗ {vid}  not found")
                bad += 1
                continue
            desc = v["snippet"].get("description", "") or ""
            has_a = CONSTANTS_MARKER in desc
            has_b = PHASE_B_MARKER in desc
            title = v["snippet"]["title"][:55]
            if has_a and has_b:
                print(f"  OK   {vid}  Phase A+B present  {title}")
                ok += 1
            else:
                print(f"  FAIL {vid}  PhaseA={has_a} PhaseB={has_b}  {title}")
                bad += 1
        except Exception as e:
            print(f"  FAIL {vid}  ERR: {e}")
            bad += 1
    return ok, bad


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true",
                    help="Actually push updates to YouTube. Default is dry-run preview.")
    ap.add_argument("--limit", type=int, default=5,
                    help="Max videos to process this run (default: 5 = canary).")
    ap.add_argument("--offset", type=int, default=0,
                    help="Skip the first N candidates (use for paging through the catalog).")
    ap.add_argument("--verify", action="store_true",
                    help="After processing, re-fetch the live videos and confirm changes landed.")
    ap.add_argument("--verify-only", action="store_true",
                    help="Skip processing; just verify the most-recent N completed videos.")
    args = ap.parse_args()

    yt = YouTubeClient()

    # ── Verify-only mode ───
    if args.verify_only:
        completed, skipped, errored, recent = load_checkpoint()
        if not recent:
            print("No recent completions on record. Run a live batch first.")
            return
        sample = recent[-args.limit:]
        ok, bad = verify_videos(yt, sample)
        print(f"\nVerify result: {ok}/{ok+bad} confirmed. {'PASS' if bad == 0 else 'FAIL — investigate before scaling'}")
        return

    # ── Anthropic client ───
    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("ERROR: ANTHROPIC_API_KEY not set in .env or environment.")
    client_anth = anthropic.Anthropic()

    # ── Load candidate list ───
    with CSV_PATH.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    candidates_all = [r for r in rows if r["video_id"] not in DELETED_IDS]
    completed, skipped, errored, recent = load_checkpoint()
    todo = [r for r in candidates_all
            if r["video_id"] not in completed
            and r["video_id"] not in skipped][args.offset : args.offset + args.limit]

    print(f"Mode:          {'LIVE' if args.live else 'DRY-RUN preview'}")
    print(f"Candidates:    {len(candidates_all)} total, {len(todo)} this run "
          f"(offset={args.offset}, limit={args.limit})")
    print(f"Prior state:   completed={len(completed)} skipped={len(skipped)} errored={len(errored)}")
    print("=" * 78)

    if not todo:
        print("Nothing to process. Either all done, or offset is past the end.")
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"aeo-phase-b-{time.strftime('%Y-%m-%d')}.log"
    log_lines = []

    quota_hit = False
    processed_now = []
    cache_creation_total = 0
    cache_read_total = 0
    input_tokens_total = 0
    output_tokens_total = 0

    for i, row in enumerate(todo, 1):
        vid = row["video_id"]
        title = row["title"]
        duration_iso = row.get("duration", "")
        duration_s = parse_iso_duration(duration_iso)

        try:
            # Fetch live state — Phase A status, current desc, recent edits all matter
            video = yt.get_video(vid)
            if not video:
                skipped.add(vid)
                print(f"  [{i:>2}/{len(todo)}] SKIP   {vid}  not found")
                continue
            current_desc = video["snippet"].get("description", "") or ""
            live_title = video["snippet"]["title"]

            if is_phase_b_done(current_desc):
                completed.add(vid)
                print(f"  [{i:>2}/{len(todo)}] DONE   {vid}  already has Phase B marker")
                continue
            if not has_phase_a(current_desc):
                # Skip — Phase A is a prerequisite. Don't silently re-do A here.
                skipped.add(vid)
                print(f"  [{i:>2}/{len(todo)}] SKIP   {vid}  no Phase A marker (run aeo-bulk-update.py first)")
                continue

            transcript = fetch_transcript(vid)
            if not transcript or len(transcript.strip()) < 60:
                skipped.add(vid)
                print(f"  [{i:>2}/{len(todo)}] SKIP   {vid}  transcript unavailable / too short")
                continue

            content, usage = call_claude(client_anth, live_title, transcript, duration_s)
            cache_creation_total += getattr(usage, "cache_creation_input_tokens", 0) or 0
            cache_read_total += getattr(usage, "cache_read_input_tokens", 0) or 0
            input_tokens_total += getattr(usage, "input_tokens", 0) or 0
            output_tokens_total += getattr(usage, "output_tokens", 0) or 0

            phase_b_block = build_phase_b_block(content)
            new_desc = splice_description(current_desc, phase_b_block)

            short_title = live_title[:55]
            print(f"  [{i:>2}/{len(todo)}] {'PUSH ' if args.live else 'DRAFT'}  {vid}  {short_title}")
            print(f"        ANSWER: {content['one_sentence_answer'][:100]}...")
            print(f"        Q×{len(content['qa'])}  TS×{len(content.get('timestamps', []))}  "
                  f"LEN={len(new_desc)}/{YT_DESC_MAX}")

            log_lines.append("=" * 78)
            log_lines.append(f"{vid}  {short_title}")
            log_lines.append(f"  duration: {duration_s}s")
            log_lines.append(f"  one_sentence_answer: {content['one_sentence_answer']}")
            log_lines.append(f"  new_desc length: {len(new_desc)}")
            log_lines.append("\n--- NEW DESCRIPTION ---\n" + new_desc + "\n")

            if args.live:
                yt.update_video(vid, description=new_desc)
                completed.add(vid)
                processed_now.append(vid)
                time.sleep(0.5)  # gentle pacing under YT quota
            else:
                # Dry-run: don't mark complete, just preview
                pass

        except json.JSONDecodeError as e:
            errored.add(vid)
            print(f"  [{i:>2}/{len(todo)}] ERR    {vid}  Claude returned non-JSON: {e}")
        except Exception as e:
            err_str = str(e)
            if any(s in err_str for s in ("quotaExceeded", "rateLimitExceeded", "userRateLimitExceeded")):
                print(f"  [{i:>2}/{len(todo)}] QUOTA  {vid}  YT quota exhausted, saving checkpoint and exiting")
                quota_hit = True
                break
            errored.add(vid)
            print(f"  [{i:>2}/{len(todo)}] ERR    {vid}  {e}")

        if args.live and i % 5 == 0:
            recent.extend(processed_now[-5:])
            save_checkpoint(completed, skipped, errored, recent)

    # Always persist skipped/errored sets — deleted-not-found videos and
    # missing-Phase-A videos won't change between runs, so we want to skip past
    # them on re-runs even after a dry-run. completed is only added in the live
    # branch above, so this is safe to call in dry-run too.
    if args.live:
        recent.extend(processed_now)
    save_checkpoint(completed, skipped, errored, recent)

    if log_lines:
        log_path.write_text("\n".join(log_lines), encoding="utf-8")

    print("=" * 78)
    print(f"Run summary ({'LIVE' if args.live else 'DRY-RUN'}):")
    print(f"  Processed this run:      {len(processed_now)}")
    print(f"  Cumulative completed:    {len(completed)} / {len(candidates_all)}")
    print(f"  Skipped:                 {len(skipped)}  Errored: {len(errored)}")
    print(f"  Anthropic tokens:        in={input_tokens_total}  out={output_tokens_total}  "
          f"cache_write={cache_creation_total}  cache_read={cache_read_total}")
    if not args.live:
        print(f"\n  DRY-RUN — no YT writes. Full preview log: {log_path}")
        print(f"  Re-run with --live to actually push.")
    elif quota_hit:
        print(f"\n  YT quota exhausted. Resume tomorrow (PT midnight reset).")

    if args.live and args.verify and processed_now:
        ok, bad = verify_videos(yt, processed_now)
        print(f"\nVerify: {ok}/{ok+bad} confirmed. "
              f"{'PASS — safe to scale up.' if bad == 0 else 'FAIL — investigate before scaling.'}")


if __name__ == "__main__":
    main()
