"""Correct Whisper's phonetic spellings of biblical/ancient proper nouns in the caption
word list before the ASS subtitles are written.

Captions come from Whisper transcribing the TTS audio (transcribe.py), so even when the
narration is pronounced correctly, Whisper spells obscure names by ear: Cush -> "Kush",
Eridu -> "Eridoo", Hiddekel -> "Hittacle". This maps those mis-hearings back to the canonical
spelling WITHOUT touching word timing — we only swap the text of each word token.

The map is intentionally scoped to names that essentially never appear in this channel's
narration in any other sense (a Bible documentary will not legitimately say "Eric" or "Kush"),
so a blanket case-insensitive swap is safe here. Extend GLOSSARY as new videos surface new
mis-hearings; keep keys lowercase and alphanumeric (matching strips surrounding punctuation).
"""
import json
import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_USER_PATH = _HERE / "caption_glossary.json"  # optional per-project overrides/extensions

# key = lowercased phonetic form Whisper emits; value = canonical spelling to display.
GLOSSARY: dict[str, str] = {
    "kush": "Cush",
    "cush": "Cush",
    "eridoo": "Eridu",
    "eridu": "Eridu",
    "hittacle": "Hiddekel",
    "hitakel": "Hiddekel",
    "hidekel": "Hiddekel",
    "hiddekel": "Hiddekel",
    "hiddakel": "Hiddekel",
    "hiddakell": "Hiddekel",
    "shunar": "Shinar",
    "shinar": "Shinar",
    "shienar": "Shinar",
    "eric": "Erech",
    "errek": "Erech",
    "erech": "Erech",
    "akhad": "Accad",
    "akkad": "Accad",
    "accad": "Accad",
    "gihon": "Gihon",
    "hiddikel": "Hiddekel",
    "dravidian": "Dravidian",
    "dravidians": "Dravidians",
    "mesopotamia": "Mesopotamia",
    "chaldees": "Chaldees",
    "nimrod": "Nimrod",
    "sankore": "Sankore",
    "djinguereber": "Djinguereber",
}


def _load() -> dict[str, str]:
    g = dict(GLOSSARY)
    if _USER_PATH.exists():
        try:
            extra = json.loads(_USER_PATH.read_text(encoding="utf-8"))
            for k, v in extra.items():
                g[k.lower()] = v
        except Exception as e:  # pragma: no cover - non-fatal
            print(f"  [glossary] could not load {_USER_PATH.name}: {e}")
    return g


_WORD_RE = re.compile(r"([^\W\d_]+)", re.UNICODE)


def _fix_token(token: str, glossary: dict[str, str]) -> str:
    """Replace the alphabetic core of a token if it is in the glossary, preserving the
    token's leading space and any trailing/leading punctuation."""
    m = _WORD_RE.search(token)
    if not m:
        return token
    core = m.group(1)
    repl = glossary.get(core.lower())
    if not repl or repl == core:
        return token
    return token[: m.start(1)] + repl + token[m.end(1):]


def correct_words(words: list[dict]) -> tuple[list[dict], int]:
    """Return (corrected_words, num_changed). Mutates copies, not the input dicts."""
    glossary = _load()
    out = []
    changed = 0
    for w in words:
        nw = dict(w)
        fixed = _fix_token(nw.get("word", ""), glossary)
        if fixed != nw.get("word", ""):
            changed += 1
        nw["word"] = fixed
        out.append(nw)
    return out, changed


def correct_by_scene(words_by_scene: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """Apply correct_words to every scene; print a one-line summary."""
    result = {}
    total = 0
    for sid, words in words_by_scene.items():
        fixed, n = correct_words(words)
        result[sid] = fixed
        total += n
    if total:
        print(f"Caption glossary: corrected {total} proper-noun spelling(s).")
    return result
