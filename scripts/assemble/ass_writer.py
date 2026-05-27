"""
Generate ASS subtitle files with per-word karaoke color overrides (Approach B).

Each word becomes yellow when reached, snaps back to gray when the next word
starts. Matches JSON2Video's 'classic' snap-color style.

ASS color format is BGR hex: yellow #FFFF00 → &H00FFFF&, gray #CCCCCC → &HCCCCCC&.
"""
from pathlib import Path

# Colors as ASS BGR hex
YELLOW = "&H00FFFF&"   # #FFFF00 in RGB
GRAY   = "&HCCCCCC&"   # #CCCCCC in RGB
BLACK  = "&H00000000&" # outline / shadow

# Words per subtitle line by aspect
WORDS_PER_LINE = {"16x9": 4, "9x16": 3}

# Font size by aspect
FONT_SIZE = {"16x9": 80, "9x16": 64}

# PlayRes by aspect
PLAY_RES = {"16x9": (1920, 1080), "9x16": (1080, 1920)}


def _cs(seconds: float) -> int:
    """Convert seconds to ASS centiseconds (integer)."""
    return max(0, round(seconds * 100))


def _ts(seconds: float) -> str:
    """Format seconds as ASS timestamp H:MM:SS.cs"""
    cs_total = round(seconds * 100)
    cs = cs_total % 100
    s_total = cs_total // 100
    s = s_total % 60
    m = (s_total // 60) % 60
    h = s_total // 3600
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def _ass_header(aspect: str) -> str:
    res_x, res_y = PLAY_RES[aspect]
    font_size = FONT_SIZE[aspect]
    return (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        f"PlayResX: {res_x}\n"
        f"PlayResY: {res_y}\n"
        "ScaledBorderAndShadow: yes\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Default,Oswald Bold,{font_size},{GRAY},{GRAY},"
        f"{BLACK},{BLACK},-1,0,0,0,100,100,0,0,1,8,6,2,20,20,80,1\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )


def _chunk_words(
    words: list[dict],
    chunk_size: int,
    scene_offset: float,
) -> list[tuple[float, float, list[dict]]]:
    """
    Split words into lines of up to chunk_size words.
    Break early on sentence-ending punctuation or on commas with >200ms gap.
    Returns list of (chunk_start, chunk_end, [word_dicts]) with absolute times.
    """
    if not words:
        return []

    chunks = []
    current: list[dict] = []

    def flush():
        if current:
            chunks.append(current[:])
            current.clear()

    for i, w in enumerate(words):
        current.append(w)
        text = w["word"]
        is_sentence_end = text and text[-1] in ".?!"
        is_comma_pause = (
            text.endswith(",")
            and i + 1 < len(words)
            and (words[i + 1]["start"] - w["end"]) > 0.2
        )
        if len(current) >= chunk_size or is_sentence_end or is_comma_pause:
            flush()

    flush()

    result = []
    for chunk in chunks:
        start = chunk[0]["start"] + scene_offset
        end = chunk[-1]["end"] + scene_offset
        offset_chunk = [
            {"word": w["word"], "start": w["start"] + scene_offset, "end": w["end"] + scene_offset}
            for w in chunk
        ]
        result.append((start, end, offset_chunk))

    return result


def _dialogue_line(chunk_start: float, chunk_end: float, chunk_words: list[dict]) -> str:
    """
    Build one ASS Dialogue line with per-word \\1c color overrides.
    Each word is yellow while current, gray otherwise.
    """
    text_parts = []
    for i, w in enumerate(chunk_words):
        word_text = w["word"]
        if not word_text:
            continue
        # Duration of this word in centiseconds for \\k
        if i + 1 < len(chunk_words):
            duration_s = chunk_words[i + 1]["start"] - w["start"]
        else:
            duration_s = w["end"] - w["start"]
        cs = _cs(duration_s)
        # Yellow while active, then snap back to gray
        text_parts.append(
            f"{{\\1c{YELLOW}\\k{cs}}}{word_text}{{\\1c{GRAY}}}"
        )
    text = " ".join(text_parts)
    start_ts = _ts(chunk_start)
    end_ts = _ts(chunk_end)
    return f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{text}\n"


def write_scene_ass(
    scene_id: str,
    words: list[dict],
    out_path: Path,
    aspect: str,
    scene_offset: float = 0.0,
) -> Path:
    """
    Write ASS for a single scene. scene_offset shifts all timestamps by that many
    seconds (used when merging into a multi-scene file).
    """
    chunk_size = WORDS_PER_LINE.get(aspect, 4)
    header = _ass_header(aspect)
    chunks = _chunk_words(words, chunk_size, scene_offset)
    lines = [_dialogue_line(s, e, ws) for s, e, ws in chunks]
    out_path.write_text(header + "".join(lines), encoding="utf-8")
    return out_path


def write_merged_ass(
    scenes: list[dict],
    words_by_scene: dict[str, list[dict]],
    audio_durations: dict[str, float],
    out_path: Path,
    aspect: str,
) -> Path:
    """
    Write a single merged ASS file covering all scenes back-to-back.
    Timestamps are absolute across the full video.
    """
    chunk_size = WORDS_PER_LINE.get(aspect, 4)
    header = _ass_header(aspect)

    all_dialogue = []
    cumulative_offset = 0.0

    for scene in scenes:
        sid = scene["scene_id"]
        words = words_by_scene.get(sid, [])
        duration = audio_durations.get(sid, 0.0)
        chunks = _chunk_words(words, chunk_size, cumulative_offset)
        for chunk_start, chunk_end, chunk_words in chunks:
            all_dialogue.append(_dialogue_line(chunk_start, chunk_end, chunk_words))
        cumulative_offset += duration

    out_path.write_text(header + "".join(all_dialogue), encoding="utf-8")
    return out_path
