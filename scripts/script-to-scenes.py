"""
Convert authored Script Format v2 .txt → scenes.json files for the ai-bible-gospels
custom-script pipeline. Bypasses the Claude AI scene-generator that paraphrases
verbatim scripture; lets us inject exact narration + image prompts.

Format spec: docs/script-format-v2.md
Schema target: C:/Users/Claude/ai-bible-gospels/workflows/custom-script/generate.py
               (line 320 — accepts {"scenes": [...]} via `generate.py scenes.json`)

Usage:
  python scripts/script-to-scenes.py drafts/edom-genesis49-longform-2026-05-16.txt \
      --out-dir output/scenes/

  python scripts/script-to-scenes.py drafts/edom-genesis49-longform-2026-05-16.txt \
      --first-n 1 --out-dir output/scenes/      # one-scene test render
"""

import argparse
import json
import re
import sys
from pathlib import Path

ALLOWED_MOTIONS = {"zoom-in", "zoom-out", "ken-burns", "pan-right", "pan-left"}

# Hard-block list — visual cues containing these patterns FAIL CONVERSION with
# a loud error. Source MUST be rewritten before re-converting. These patterns
# have been documented to produce inappropriate / unintended renders that
# violate the channel's brand and audience expectations.
#
# Locked 2026-05-17 per Tommy after the Jacob+Joseph mountaintop scene
# rendered as two men in a kiss-like pose. The "embracing" language combined
# with golden cinematic mountaintop cinematography produced unacceptable
# imagery. From this point forward: any source .txt visual cue containing
# these patterns blocks conversion until rewritten.
BLOCKED_VISUAL_PATTERNS = (
    "embracing", "embrace", "embraced",
    "kissing", "kiss", "kissed",
    "intimate contact", "intimately",
    "face-to-face", "face to face",
    "lips touching", "lips meeting",
    "romantic", "romantically",
    "lovers",
)
BLOCKED_RE = re.compile(
    r"\b(" + "|".join(re.escape(p) for p in BLOCKED_VISUAL_PATTERNS) + r")\b",
    re.IGNORECASE,
)

DEFAULT_MOTION = "ken-burns"
DEFAULT_LIGHTING = "Deep navy chiaroscuro with golden divine amber light"

# Identity keywords that, when present, signal the scene is already strongly
# tagged as Black Hebrew Israelite. Used only to skip the injection if the source
# already carries the full strong identity phrase. Weak keywords like "dark-brown"
# or "melanated" alone are NOT in this list — they're too weak to prevent FLUX
# defaulting to Caucasian features (proven failure 2026-05-16 on Edom Part 1
# render at scene 2: "dark-brown-skinned, melanated... patriarch" rendered with
# white men around the deathbed).
MELANATED_KEYWORDS = ("Black Hebrew Israelite", "Black Hebrew Israelites")

# Strong identity suffix based on proven-working prompts (per Tommy's references).
# The key phrase is "Black Hebrew Israelite" — FLUX recognizes this as a specific
# cultural identity. Adding "locs", "tzitzit fringes" reinforces. Negative prompts
# ("NOT white") have been REMOVED — they were proven to NOT prevent Caucasian
# rendering and the user's working examples don't use them.
MELANATED_SUFFIX = (
    ", Black Hebrew Israelite with rich African American complexion, "
    "deeply melanated dark brown skin, "
    "natural afro-textured hair in locs, braids, or twists, "
    "wearing earth-toned Hebrew robes with tzitzit fringes"
    # Canonical adult-male identity stack — appropriate for prophets,
    # patriarchs, warriors. NOT appropriate for babies, women, or children
    # — the "locs/braids/tzitzit fringes" descriptors override scene-
    # specific details like "red hair" or "head wrap" or "infant smooth
    # skin." For those, use LIGHT_MELANATED_SUFFIX below.
    #
    # This suffix is ALWAYS injected on every Israelite scene, even when
    # the source [Visual:] cue already contains identity language. The
    # redundancy intentionally reinforces the FLUX signal — repeated
    # emphasis = consistent rendering across every scene of every video.
    # Per Tommy 2026-05-17: "this needs to be for all scenes... whenever
    # we talk about the Israelites to make sure this is set."
)

# Lighter identity for babies, women, children. Skips beard/robes/tzitzit
# descriptors that override scene-specific markers. Proven necessary on
# 2026-05-17 after the newborn-twins render lost Esau's "red hair" detail
# because the heavy MELANATED_SUFFIX overrode it with "natural afro-textured
# hair in locs or braids".
LIGHT_MELANATED_SUFFIX = (
    ", Black Hebrew Israelite with rich African American complexion, "
    "deeply melanated dark brown skin"
)

# Triggers for the light path — when ANY of these appear in the [Visual:]
# cue, the converter uses LIGHT_MELANATED_SUFFIX instead of the heavy one.
LIGHT_IDENTITY_TRIGGERS = (
    "newborn", "newborns", "baby", "babies", "infant", "infants",
    "child", "children", "kid", "kids", "toddler",
    "woman", "women", "mother", "mothers", "wife", "wives",
    "girl", "girls", "daughter", "daughters",
    "pregnant", "womb", "pregnancy", "fetal", "fetus",
    "Rebekah", "Sarah", "Hagar", "Miriam", "Hannah", "Mary", "Ruth",
    "Esther", "Tamar", "Deborah", "Rachel", "Leah",
)
LIGHT_IDENTITY_RE = re.compile(
    r"\b(" + "|".join(LIGHT_IDENTITY_TRIGGERS) + r")\b", re.IGNORECASE
)

# Esau / Edom / Edomite scenes are the THEOLOGICAL OPPOSITE of Israelite scenes
# per the channel's Hebrew Israelite worldview: Jacob -> Israel -> Black, Esau ->
# Edom -> Caucasian/European. Genesis 25:25 cites Esau as "red, all over like an
# hairy garment" — the origin of the Edomite bloodline. Without this contrast,
# the "Why did Christ vow to destroy Edom" thesis collapses.
EDOM_INDICATORS = ("Esau", "Edom", "Edomite", "Edomites")
EDOM_SUFFIX = (
    ", Caucasian European with pale fair complexion, reddish-tinged skin, "
    "hairy, brown or auburn hair and beard, ancient Edomite garments, "
    "NOT African, NOT melanated, NOT Black Hebrew Israelite"
)
# Jacob mentions: when BOTH Jacob and Esau are in a scene (e.g., the pottage
# scene), the source [Visual:] cue must explicitly describe both — the
# converter does NOT auto-inject either suffix to avoid contradictions. Detected
# below and reported in the log so we know to verify the source cue is explicit.
JACOB_INDICATORS = ("Jacob",)

# 12 Tribes -> nationality markers, sourced from
# docs/tribes-to-nationalities.md (channel theology). When a tribe name
# appears in a [Visual:] cue, the converter auto-injects these markers AFTER
# the base Israelite identity suffix. This lets the user write scripts the
# same way (just "Tribe of Issachar warrior" in the visual cue) — the
# converter expands to include the Mexican/Aztec features automatically.
TRIBE_MARKERS = {
    "judah":     "from the tribe of Judah — African American features, deeply melanated dark brown skin, locs or braids, royal Lion-of-Judah sigil and gold accents when biblical",
    "benjamin":  "from the tribe of Benjamin — West Indian / Jamaican / Caribbean features, dreadlocks, vibrant traditional Caribbean fabrics",
    "levi":      "from the tribe of Levi — tall lean African features, ceremonial priestly vestments with ephod and tzitzit fringes, Torah scroll context",
    "reuben":    "from the tribe of Reuben — Seminole / Eastern Native American features with melanated skin, traditional patchwork garments",
    "simeon":    "from the tribe of Simeon — Dominican features with mixed Afro-Caribbean phenotype, deeply melanated, Hispaniola context",
    "issachar":  "from the tribe of Issachar — Aztec / Mexican features with deeply melanated skin, ancient Aztec headdress and feathered regalia, stepped temple setting",
    "zebulun":   "from the tribe of Zebulun — Mayan features with melanated skin, jade jewelry, traditional Mayan textiles, pyramid setting",
    "gad":       "from the tribe of Gad — Native American Plains features with deeply melanated skin, feathered war bonnet, lion-like stance",
    "naphtali":  "from the tribe of Naphtali — South Pacific Polynesian or Chilean features with melanated skin, coconuts and taro, South Pacific island setting",
    "asher":     "from the tribe of Asher — melanated Black Hebrew Israelite Americas-diaspora features",
    "manasseh":  "from the tribe of Manasseh — Cuban features with deeply melanated skin, Afro-Cuban phenotype",
    "ephraim":   "from the tribe of Ephraim — Puerto Rican / Boricua features with melanated skin, Caribbean aesthetic",
}
# Detect tribe references. Word-boundary match on each tribe name so we don't
# false-positive on substrings ("Levi" in "Levitical" still matches and is fine).
TRIBE_RE = re.compile(
    r"\btribe of (" + "|".join(TRIBE_MARKERS.keys()) + r")\b|"
    r"\b(" + "|".join(TRIBE_MARKERS.keys()) + r")\b",
    re.IGNORECASE,
)

# Style/camera suffix from Tommy's proven-working prompts. RED V-Raptor + skin
# texture + film grain biases FLUX toward photorealistic dark-skin rendering.
SAFETY_SUFFIX = (
    ", no text, no letters, no symbols, photorealistic, cinematic, 8K detail, "
    "shot on RED V-Raptor, hyper-detailed skin texture and fabric weave, "
    "natural film grain"
)

# Only inject melanated keywords when the visual depicts a human. Skips
# inanimate / landscape / animal scenes (sky, scrolls, lions, vineyards, etc.).
PERSON_INDICATORS = (
    "man", "woman", "men", "women", "person", "persons", "people",
    "figure", "figures", "patriarch", "prophet", "priest", "priestess",
    "king", "queen", "warrior", "warriors", "hunter", "hunters", "refugee",
    "refugees", "mason", "masons", "stonemason", "stonemasons", "soldier",
    "soldiers", "child", "children", "son", "sons", "daughter", "brother",
    "brothers", "sister", "family", "families", "captain", "captains",
    "rabbi", "shepherd",
    # named characters (KJV roster commonly used in our scripts)
    "jacob", "esau", "isaac", "rebekah", "judah", "joseph", "moses",
    "elijah", "edomite", "edomites", "hebrew", "hebrews", "israelite",
    "israelites",
)
PERSON_RE = re.compile(r"\b(" + "|".join(PERSON_INDICATORS) + r")\b", re.IGNORECASE)

SECTION_DIVIDER = re.compile(r"^={5,}\s*$")
SECTION_HEADER = re.compile(r"^\[([A-Z][^\]]*)\]\s*$")

WORD_THRESHOLD_FOR_SPLIT = 900


def parse_script(text: str):
    """Parse Script Format v2 text into (sections, scenes).

    Returns:
      sections: list of dicts {name: str, start_scene_idx: int} for split logic
      scenes: list of dicts {narration, imagePrompt, motion, lighting, _section_name, _line}
    """
    lines = text.splitlines()
    scenes = []
    sections = []

    i = 0
    n = len(lines)
    current_section = "PROLOGUE"

    # Skip header — everything before first section divider
    while i < n and not SECTION_DIVIDER.match(lines[i]):
        i += 1

    while i < n:
        line = lines[i]

        # Section divider — section name on the next non-empty line in brackets
        if SECTION_DIVIDER.match(line):
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            if j < n:
                m = SECTION_HEADER.match(lines[j].strip())
                if m:
                    current_section = m.group(1).strip()
                    sections.append({"name": current_section, "start_scene_idx": len(scenes)})
                    # Skip past the closing divider too
                    k = j + 1
                    while k < n and not SECTION_DIVIDER.match(lines[k]):
                        k += 1
                    i = k + 1
                    continue
            i += 1
            continue

        # Visual cue starts a scene
        if line.lstrip().startswith("[Visual:"):
            scene_line = i + 1  # 1-indexed
            visual, i = _read_bracket_block(lines, i, "Visual:")
            motion = None
            lighting = None

            # Look ahead for optional [Motion:] and [Lighting:]
            while i < n and (lines[i].lstrip().startswith("[Motion:") or
                             lines[i].lstrip().startswith("[Lighting:") or
                             not lines[i].strip()):
                if lines[i].lstrip().startswith("[Motion:"):
                    motion, i = _read_bracket_block(lines, i, "Motion:")
                elif lines[i].lstrip().startswith("[Lighting:"):
                    lighting, i = _read_bracket_block(lines, i, "Lighting:")
                else:
                    i += 1

            # Find Narrator: block and pull the quoted text
            while i < n and lines[i].strip() != "Narrator:":
                i += 1
            if i >= n:
                raise SyntaxError(
                    f"Scene at line {scene_line} has [Visual:] but no Narrator: block"
                )
            i += 1  # past 'Narrator:'

            # Collect the quoted narration — must start with " on its own (or leading)
            narration = _read_quoted_narration(lines, i, scene_line)
            # Advance past the narration block (consume until we hit a blank line or next [Visual:])
            while i < n:
                if lines[i].lstrip().startswith("[Visual:") or SECTION_DIVIDER.match(lines[i]):
                    break
                i += 1

            scenes.append({
                "_section_name": current_section,
                "_line": scene_line,
                "narration": narration,
                "_visual": visual,
                "_motion": motion,
                "_lighting": lighting,
            })
            continue

        i += 1

    return sections, scenes


def _read_bracket_block(lines, i, label):
    """Read a [Label: ...] block that may span multiple lines until the closing ']'.
    Returns (content_str, next_i).
    """
    line = lines[i]
    start = line.find(label) + len(label)
    chunk = line[start:].lstrip()
    j = i
    while "]" not in chunk:
        j += 1
        if j >= len(lines):
            raise SyntaxError(f"Unclosed [{label}...] at line {i+1}")
        chunk += " " + lines[j].strip()
    closing = chunk.rfind("]")
    content = chunk[:closing].strip()
    return content, j + 1


def _read_quoted_narration(lines, i, scene_line):
    """Read a quoted narration block starting at or after lines[i].

    Handles multi-line quotes. Returns the inner text (no quotes).
    """
    # Find the opening "
    while i < len(lines) and '"' not in lines[i]:
        i += 1
    if i >= len(lines):
        raise SyntaxError(f"Scene at line {scene_line}: no quoted narration found")

    line = lines[i]
    open_q = line.find('"')
    chunk = line[open_q + 1:]

    if '"' in chunk:
        # Same-line close
        close_q = chunk.find('"')
        return chunk[:close_q].strip()

    # Multi-line — collect until closing "
    parts = [chunk]
    j = i + 1
    while j < len(lines):
        if '"' in lines[j]:
            close_q = lines[j].find('"')
            parts.append(lines[j][:close_q])
            return " ".join(p.strip() for p in parts).strip()
        parts.append(lines[j])
        j += 1
    raise SyntaxError(f"Scene at line {scene_line}: unclosed quoted narration")


def build_scene_dict(scene_raw):
    """Convert parsed scene into the final pipeline-ready dict with auto-injection."""
    visual = scene_raw["_visual"]
    motion = scene_raw["_motion"] or DEFAULT_MOTION
    lighting = scene_raw["_lighting"] or DEFAULT_LIGHTING
    narration = scene_raw["narration"]

    if motion not in ALLOWED_MOTIONS:
        raise ValueError(
            f"Scene at line {scene_raw['_line']}: motion='{motion}' is not one of "
            f"{sorted(ALLOWED_MOTIONS)}. Edit the script's [Motion:] cue."
        )

    # Hard-block check: source visual cue must not contain banned patterns
    # (embracing, kiss, romantic, etc.) — these produce inappropriate renders.
    blocked = BLOCKED_RE.search(visual)
    if blocked:
        raise ValueError(
            f"Scene at line {scene_raw['_line']}: visual cue contains BLOCKED "
            f"pattern '{blocked.group(0)}'. Source must be rewritten. "
            f"See feedback memory 'visual-block-list' for context.\n"
            f"  Offending visual: {visual[:200]}..."
        )

    image_prompt = visual
    injected_melanated = False
    injected_edom = False
    needs_manual_verify = False
    injected_tribes = []
    has_person = bool(PERSON_RE.search(image_prompt))
    has_esau = any(name in image_prompt for name in EDOM_INDICATORS)
    has_jacob = any(name in image_prompt for name in JACOB_INDICATORS)

    if has_person:
        if has_esau and has_jacob:
            # Mixed-brothers scene (e.g., the pottage moment, Isaac's
            # blessing). Auto-injecting either suffix would contradict the
            # other figure. Source [Visual:] cue must explicitly cast both
            # — flag for manual verification.
            needs_manual_verify = True
        elif has_esau:
            # Pure Esau / Edom / Edomite scene → Caucasian per Hebrew Israelite
            # theology (Genesis 25:25 — Esau "red, all over like an hairy
            # garment" = Edomite bloodline = European peoples).
            image_prompt += EDOM_SUFFIX
            injected_edom = True
        else:
            # Israelite scene → Black Hebrew Israelite
            # ALWAYS inject the canonical identity, even if the source
            # already mentions "Black Hebrew Israelite" or "melanated".
            # The redundancy reinforces FLUX's identity signal — repeated
            # emphasis = consistent rendering across every scene of every
            # video. Per Tommy 2026-05-17.
            # Light path for babies/women/children (no beard/robes/tzitzit
            # descriptors that would override scene-specific markers).
            if LIGHT_IDENTITY_RE.search(image_prompt):
                image_prompt += LIGHT_MELANATED_SUFFIX
            else:
                image_prompt += MELANATED_SUFFIX
            injected_melanated = True

    # Detect 12-tribe references and auto-inject nationality markers from
    # docs/tribes-to-nationalities.md. Runs AFTER the base identity suffix so
    # tribe markers refine (not replace) the BHI identity. Edomite scenes
    # skip tribe injection (Esau is the rejected line, not a tribe). Mixed
    # brother scenes also skip — source must be explicit.
    if has_person and not has_esau and not needs_manual_verify:
        seen_tribes = set()
        for m in TRIBE_RE.finditer(image_prompt):
            tribe = (m.group(1) or m.group(2) or "").lower()
            if tribe and tribe not in seen_tribes:
                seen_tribes.add(tribe)
                # Append once per scene; if multiple tribes mentioned, append
                # markers for each (though that's unusual)
                marker = TRIBE_MARKERS.get(tribe)
                if marker:
                    image_prompt += ", " + marker
                    injected_tribes.append(tribe)

    image_prompt += SAFETY_SUFFIX

    return {
        "narration": narration,
        "imagePrompt": image_prompt,
        "motion": motion,
        "lighting": lighting,
    }, {
        "melanated": injected_melanated,
        "edom": injected_edom,
        "manual_verify": needs_manual_verify,
        "tribes": injected_tribes,
    }


def split_scenes_into_parts(sections, scenes_raw, word_threshold):
    """Split scenes into 1 or 2 parts.

    If total narration words ≤ threshold: returns [scenes_raw]
    Otherwise: splits at the last section boundary before the midpoint by word count.
    """
    word_counts = [len(s["narration"].split()) for s in scenes_raw]
    total_words = sum(word_counts)

    if total_words <= word_threshold:
        return [scenes_raw]

    midpoint = total_words / 2
    cumulative = 0
    cumulative_per_scene = []
    for wc in word_counts:
        cumulative += wc
        cumulative_per_scene.append(cumulative)

    # Find last section boundary before midpoint
    best_section_boundary = None
    for sec in sections:
        idx = sec["start_scene_idx"]
        if idx == 0:
            continue
        words_before = cumulative_per_scene[idx - 1] if idx > 0 else 0
        if words_before <= midpoint:
            best_section_boundary = idx
        else:
            break

    if best_section_boundary is None or best_section_boundary == 0:
        # Fallback: split at exact midpoint scene
        for idx, c in enumerate(cumulative_per_scene):
            if c >= midpoint:
                best_section_boundary = idx + 1
                break

    return [scenes_raw[:best_section_boundary], scenes_raw[best_section_boundary:]]


def derive_base_name(script_path: Path) -> str:
    """Derive a clean base name from the script file path."""
    name = script_path.stem
    # Strip date suffix like -2026-05-16
    name = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", name)
    # Strip type suffix like -longform
    name = re.sub(r"-longform$", "", name)
    return name


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("script_file", help="Path to the .txt script (Script Format v2)")
    parser.add_argument("--out-dir", default="output/scenes", help="Output directory for scenes JSON")
    parser.add_argument("--first-n", type=int, default=None,
                        help="Emit only the first N scenes (for cheap single-scene test renders)")
    parser.add_argument("--no-split", action="store_true",
                        help="Do not auto-split long scripts into part1/part2")
    args = parser.parse_args()

    script_path = Path(args.script_file).resolve()
    if not script_path.exists():
        print(f"ERROR: {script_path} not found", file=sys.stderr)
        sys.exit(1)

    text = script_path.read_text(encoding="utf-8")
    sections, scenes_raw = parse_script(text)

    if not scenes_raw:
        print(f"ERROR: no scenes parsed from {script_path}", file=sys.stderr)
        sys.exit(1)

    # Build the pipeline-ready scenes + collect injection log
    built = []
    melanated_lines = []
    edom_lines = []
    verify_lines = []
    tribe_hits = []  # list of (line, [tribes])
    for s in scenes_raw:
        d, flags = build_scene_dict(s)
        built.append(d)
        if flags["melanated"]:
            melanated_lines.append(s["_line"])
        if flags["edom"]:
            edom_lines.append(s["_line"])
        if flags["manual_verify"]:
            verify_lines.append(s["_line"])
        if flags.get("tribes"):
            tribe_hits.append((s["_line"], flags["tribes"]))

    # Trim to first-N if requested
    if args.first_n is not None:
        built = built[: args.first_n]
        scenes_raw = scenes_raw[: args.first_n]

    # Split if needed
    if args.no_split or args.first_n is not None:
        parts = [built]
    else:
        # We need to split on the BUILT scenes too — use the raw narration words for sizing
        parts_raw = split_scenes_into_parts(sections, scenes_raw, WORD_THRESHOLD_FOR_SPLIT)
        if len(parts_raw) == 1:
            parts = [built]
        else:
            split_at = len(parts_raw[0])
            parts = [built[:split_at], built[split_at:]]

    # Write outputs
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = derive_base_name(script_path)
    if args.first_n is not None:
        out_paths = [out_dir / f"{base}-first{args.first_n}-scenes.json"]
    elif len(parts) == 1:
        out_paths = [out_dir / f"{base}-scenes.json"]
    else:
        out_paths = [out_dir / f"{base}-part{i+1}-scenes.json" for i in range(len(parts))]

    for path, scenes in zip(out_paths, parts):
        words = sum(len(s["narration"].split()) for s in scenes)
        path.write_text(json.dumps({"scenes": scenes}, indent=2, ensure_ascii=False),
                        encoding="utf-8")
        print(f"  Wrote {len(scenes):>3} scenes ({words:>4} words) -> {path}")

    # Injection log
    print()
    if melanated_lines:
        print(f"  Auto-injected Black Hebrew Israelite stack on scenes at lines: {melanated_lines}")
    if edom_lines:
        print(f"  Auto-injected Caucasian Edomite stack on scenes at lines: {edom_lines}")
    if verify_lines:
        print(f"  [WARN] MIXED-BROTHERS scenes at lines (verify source describes both Jacob AND Esau "
              f"explicitly - converter skipped auto-injection to avoid contradictions): {verify_lines}")
    if tribe_hits:
        print(f"  Tribe-marker injections (from docs/tribes-to-nationalities.md):")
        for line, tribes in tribe_hits:
            print(f"    line {line}: {', '.join(tribes)}")
    if not (melanated_lines or edom_lines or verify_lines):
        print(f"  No auto-injections needed — all {len(scenes_raw)} scenes already strongly tagged")

    print(f"\nDone. Total: {len(scenes_raw)} scenes, "
          f"{sum(len(s['narration'].split()) for s in built)} narration words.")


if __name__ == "__main__":
    main()
