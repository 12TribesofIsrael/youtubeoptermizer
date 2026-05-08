"""Convert src/anchor-doc/src/subtitles.json into a YouTube-uploadable .srt
caption track. Output: src/anchor-doc/out/anchor-doc.srt
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "anchor-doc" / "src" / "subtitles.json"
OUT = ROOT / "src" / "anchor-doc" / "out" / "anchor-doc.srt"


def to_timecode(secs: float) -> str:
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = secs - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


cues = json.loads(SRC.read_text(encoding="utf-8"))
lines = []
for i, cue in enumerate(cues, 1):
    lines.append(str(i))
    lines.append(f"{to_timecode(cue['start'])} --> {to_timecode(cue['end'])}")
    lines.append(cue["text"])
    lines.append("")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote {len(cues)} cues to {OUT.relative_to(ROOT)}")
