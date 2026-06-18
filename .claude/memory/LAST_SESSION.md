---
name: ""
metadata: 
  node_type: memory
  ended: 2026-06-17T00:00:00Z
  project: youtubeoptermizer (AI Bible Gospels YT optimization)
  branch: main
  originSessionId: 38ede334-c627-463f-ae37-a68d5a7de7b3
---

# Last Session — 2026-06-17

## What the user wanted
Turn `docs/frombabylontotimbuktu.md` (a raw, unpunctuated YouTube auto-transcript of Windsor's book) into a narration-ready audiobook for the channel — then, once copyright blocked that, pivot to an ORIGINAL ~2-hour flagship comeback documentary covering the whole book's arc, for Speechify→Remotion→YouTube.

## What we did
- Found the source file was chapters 1–4 of Windsor tripled; deduped + punctuated → `docs/frombabylontotimbuktu-narration.md` and `-speechify.txt` (now gitignored).
- Downloaded full archive.org OCR (`docs/fbtt_raw_djvu.txt`); tried to clean/format the full book via sub-agents — **blocked**: book is copyrighted (1969, ~2064), AND Anthropic's content filter hard-blocks bulk verbatim reproduction (3×). User said "I have rights" but provided no clearance doc; verbatim path is closed regardless via the filter.
- **Pivoted to original work**: wrote `docs/fbtt-original-episode-script.md` — original ~2hr documentary "From Eden to Timbuktu" (Cold Open + Intro + 8 Parts incl. **Part 5: Lineage of the Messiah, Abraham→Christ via Matthew 1** + Conclusion). ~15,150 narration words. Cites Windsor as source, NOT a reproduction. Brand `[SCENE]` cues + KJV scripture + anti-extremism guardrail in conclusion.
- Generated `docs/fbtt-eden-to-timbuktu-speechify.txt` via a transform script (scene cues stripped, no markdown, no digits, spoken chapter announcements). ~15,033 words.
- Gitignored the copyrighted book files; committed script+narration (`9dc3d7d`); later added `docs/audio/` ignore rule (`8c05443`). All pushed to origin/main.
- Used the genealogy chart `docs/Genealogy_of_Jesus_pictures2-locked.pdf` (ESV, copyrighted) only as a reference for the Matthew 1 chain.
- Scoped a repo cleanup (Explore agents mapped clutter + path deps) but user deferred it.

## Decisions worth remembering
- Original-prose pivot is the durable strategy for book-based content (copyright + content-filter both block verbatim). See [[feedback_fbtt_copyright_not_public_domain]].
- Did NOT untrack `docs/Genealogy_..._locked.pdf` (still tracked) — user deferred cleanup.

## Open threads / next session starts here
- **Repo cleanup (deferred, user said "don't worry about clean up now")**: safe wins when resumed — delete local-only scratch (~24 root `testing-*.png`/`tiktok-*.png`/`tmp_*`/`tictok.mp4`, `__pycache__/`, ~40 `analytics/_tt-*`/`_tiktok-*` debug files); `git rm --cached docs/Genealogy_of_Jesus_pictures2-locked.pdf`; optionally reorganize `docs/` into topic subfolders (update CLAUDE.md/README links). DO NOT move `scripts/` (27 files hardcode `sys.path` parent.parent), `analytics/`, `output/`, `training/`, `faith-walk-live/`, `static/`, `templates/`, OAuth files, or `scripts/assemble/` — all pinned by code.
- Script still needs: final KJV verse verification vs `docs/1611KjvW_apocrypha - Copy.pdf`; user then runs Speechify (Daniel voice `onwK4e9ZLuTAKqWW03F9`) → MP3 → Remotion/CapCut.
- 119 MB narration MP3 lives in `docs/audio/` (now gitignored) — exceeds GitHub 100MB limit, keep local.

## Uncommitted work
Clean working tree.
