"""Parse drafts/eden-full-doc-scene-plan.md into a structured scene manifest.

The scene plan is the human-authored source of truth for Parts Two-Eight + Conclusion + CTA.
This turns it into output/manifests/eden-full-scenes.json so the generators
(cards/visuals/kling) and the assembler all read one machine-checked structure
instead of re-parsing prose.

Deliberately strict: any scene that fails to yield an id/source/mood/narration is a hard
error, not a silent skip. A silently-dropped scene means a silently-missing 60s of film.

Usage: python scripts/parse-scene-plan.py [--check]
Output: output/manifests/eden-full-scenes.json
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "drafts" / "eden-full-doc-scene-plan.md"
SFX_MAP = ROOT / "scripts" / "assemble" / "sfx_map.json"
OUT = ROOT / "output" / "manifests" / "eden-full-scenes.json"


def _load_converter():
    """Import scripts/script-to-scenes.py (hyphens block a normal import).

    The converter IS the canonical identity framework — PERSON_RE, the blocked-pose
    list, and the identity suffixes live there and only there. Never re-declare them
    here; a second copy is a second thing to drift.
    """
    spec = importlib.util.spec_from_file_location("s2s", ROOT / "scripts" / "script-to-scenes.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S2S = _load_converter()
PERSON_RE = S2S.PERSON_RE
LIGHT_ID_RE = S2S.LIGHT_IDENTITY_RE
BLOCKED_RE = S2S.BLOCKED_RE

VALID_SOURCES = {"KLING", "CARD", "MAP", "STILL", "ARCHIVAL"}

# Scene header:  - **p4_2 | KLING | ancient-river** ⭐ FIGURE
#                - **p2_1 | CARD | desert-wind** — Chapter card: "II. ..."
HEADER_RE = re.compile(r"^- \*\*([a-z0-9_]+) \| ([A-Z]+) \| ([a-z-]+)\*\*(.*)$")
FIELD_RE = re.compile(r"^\s*(Narration|Visual|Kling):\s*(.*)$")

# Part headings drive ordering + grouping.
PART_RE = re.compile(r"^## (PART [A-Z]+|CONCLUSION|CALL TO ACTION)\b.*$")


def parse():
    text = PLAN.read_text(encoding="utf-8")
    valid_moods = set(json.loads(SFX_MAP.read_text(encoding="utf-8"))["moods"])

    scenes = []
    part = None
    cur = None
    field = None
    errors = []

    for lineno, line in enumerate(text.splitlines(), 1):
        m_part = PART_RE.match(line)
        if m_part:
            part = m_part.group(0).lstrip("# ").strip()
            continue

        m_head = HEADER_RE.match(line)
        if m_head:
            if cur:
                scenes.append(cur)
            sid, source, mood, tail = m_head.groups()
            # The header tail carries the card copy for chapter cards, e.g.
            #   - **p2_1 | CARD | desert-wind** — Chapter card: "II. The Origin of the Nations."
            # Dropping it fed gpt-image-1 the Visual line's transition note instead, and the
            # canary rendered "MOUNT ARARAT" on what should have been the chapter title.
            # Keep it: for CARD scenes it is the text to set, not a note about the text.
            # Only a quoted chapter title is literal copy. Bare parentheticals like
            # "(scripture card — Matthew 1:1)" are type annotations for the reader — setting
            # those as card text would print the annotation onto the card. Those scenes carry
            # their copy in the Visual line instead, which is the correct fallback.
            m_title = re.search(r'Chapter card:\s*[""«]?([^""»]+)[""»]?', tail)
            note = m_title.group(1).strip().rstrip(".") if m_title else ""
            cur = {
                "id": sid,
                "part": part,
                "source": source,
                "sfx_mood": mood,
                "narration": "",
                "visual": "",
                "card_text": note if source == "CARD" else "",
                "figure": "FIGURE" in tail,
                "line": lineno,
            }
            field = None
            if source not in VALID_SOURCES:
                errors.append(f"L{lineno} {sid}: unknown source {source!r}")
            if mood not in valid_moods:
                errors.append(f"L{lineno} {sid}: mood {mood!r} not in sfx_map.json")
            continue

        if cur is None:
            continue

        m_field = FIELD_RE.match(line)
        if m_field:
            name, rest = m_field.groups()
            field = "narration" if name == "Narration" else "visual"
            cur[field] = rest.strip()
            continue

        # Continuation of the current field (wrapped prose).
        if field and line.strip() and not line.startswith(("#", "---", "- **")):
            cur[field] = (cur[field] + " " + line.strip()).strip()
        elif line.startswith(("---", "## ")):
            field = None

    if cur:
        scenes.append(cur)

    # Strip the surrounding quotes the plan uses for narration.
    for s in scenes:
        n = s["narration"].strip()
        if len(n) >= 2 and n[0] == '"' and n[-1] == '"':
            n = n[1:-1]
        s["narration"] = n.strip()

    # Resolve the identity stack EXPLICITLY rather than letting the converter's
    # keyword heuristic guess. script-to-scenes.py injects MELANATED_SUFFIX on any
    # scene with a person and no "Esau" — which would render Part Two's Blumenbach
    # and the northern migration as Black Hebrew Israelites and invert the whole
    # argument. The plan marks those scenes "[EDOM" / "[EDOM/JAPHETH RULE"; that
    # marker is the authority here, not keyword detection.
    # An explicit "no figures" / "abstract" / "no face" direction always wins over keyword
    # detection. PERSON_RE fires on words like "family" and "figure" that appear in purely
    # abstract cues ("one family, many complexions"; "a figure of light") — on 2026-07-16 that
    # put a robed man with locs into p2_7, a scene specified as pure light and no figures, and
    # would have rendered a FACE on the glorified Messiah in p5_8. Note "NO FACIAL FEATURES"
    # does not contain "NO FACE" as a word — match the stem, not the word.
    ABSTRACT_RE = re.compile(
        r"\bno figures?\b|\bno people\b|\bno close figures\b|\babstract\b|"
        r"\bno fac\w*\b|do not render (the |a )?fac\w*|"
        r"only radiance|silhouette (and|only)|light and majesty",
        re.I,
    )
    for s in scenes:
        v = s["visual"]
        if "[EDOM" in v.upper():
            s["identity"] = "european"
        elif ABSTRACT_RE.search(v):
            s["identity"] = "none"          # abstract graphics + divine figures: no identity stack
        elif s["source"] in ("CARD", "MAP"):
            s["identity"] = "none"          # text cards and maps carry no figures
        elif PERSON_RE.search(v):
            s["identity"] = "light" if LIGHT_ID_RE.search(v) else "melanated"
        else:
            s["identity"] = "none"

    # Hard validation — a missing field is a missing minute of film.
    seen = set()
    for s in scenes:
        if s["id"] in seen:
            errors.append(f"{s['id']}: duplicate id")
        seen.add(s["id"])
        if not s["narration"]:
            errors.append(f"{s['id']} (L{s['line']}): no narration")
        if not s["visual"]:
            errors.append(f"{s['id']} (L{s['line']}): no visual direction")
        if s["source"] == "KLING" and not s["figure"]:
            errors.append(f"{s['id']}: KLING scene not marked FIGURE")
        # Blocked-pose gate, same list the converter enforces. A visual cue that
        # reads as intimate-coded must be rewritten at the source, never shipped.
        blocked = BLOCKED_RE.search(s["visual"])
        if blocked:
            errors.append(
                f"{s['id']} (L{s['line']}): BLOCKED visual pattern {blocked.group(0)!r} "
                f"— rewrite the cue (see memory 'visual-block-list')"
            )

    return scenes, errors


def main():
    scenes, errors = parse()

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    words = sum(len(s["narration"].split()) for s in scenes)
    by_source = {}
    for s in scenes:
        by_source[s["source"]] = by_source.get(s["source"], 0) + 1

    print(f"scenes      : {len(scenes)}")
    print(f"by source   : {by_source}")
    print(f"narration   : {words:,} words (~{words/175:.1f} min at 175 wpm)")
    print(f"kling       : {[s['id'] for s in scenes if s['source']=='KLING']}")

    if "--check" in sys.argv:
        print("\n--check: parsed clean, nothing written.")
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"scenes": scenes}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
