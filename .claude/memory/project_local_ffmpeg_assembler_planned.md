---
name: local-ffmpeg-assembler-planned
description: "Local FFmpeg assembler to replace JSON2Video in Custom Script 2.0 — designed 2026-05-18, kickoff \"this week\", ~1 day work, ~$1-2/video savings + dependency removal"
metadata: 
  node_type: memory
  type: project
  originSessionId: c9699ade-565d-4b46-a93a-a2cf423ab18d
---

A local-only FFmpeg-based video assembler that replaces JSON2Video as the last-mile step in the Custom Script 2.0 pipeline. Ingests 16 Kling clip URLs + narration text → produces the same branded MP4 (Daniel TTS audio, Oswald-Bold yellow-current-word karaoke subs burned in) locally.

**Status as of 2026-05-18:** Design complete, NOT implemented. User explicitly chose "document, don't build" — kickoff scheduled "this week". Doc committed and pushed as 792a805. Single source of truth: [`docs/local-ffmpeg-assembler.md`](docs/local-ffmpeg-assembler.md).

**Why:** Currently paying JSON2Video ~$1.50/video for assembly. Net savings going local is ~$1-2/video (NOT $3-4 — corrected during session; real ElevenLabs cost is ~$3-5/render on `eleven_multilingual_v2` for 20-min long-form). Bigger lever is dependency removal: no third-party render outage can stall production.

**How to apply:**
- When the user says "let's kick off the local assembler" / "let's build the FFmpeg tool", read `docs/local-ffmpeg-assembler.md` first — it has the full module layout, FFmpeg two-pass command sketches, ASS Approach B (`\1c` per-word color override) pattern, risk list, and 1-scene canary verification protocol.
- **Task zero before any feature code:** install FFmpeg (verified NOT on PATH as of 2026-05-18) and add `faster-whisper`, `av`, `requests` to [`requirements.txt`](requirements.txt).
- **Repo location is locked:** youtubeoptermizer (not ai-bible-gospels, not a new repo). All building blocks already here. ai-bible-gospels is READ-ONLY per [[feedback_repo_scope]].
- **Upstream dependency:** ai-bible-gospels needs a `--skip-json2video` flag added to `workflows/custom-script/generate.py` to dump `clips_manifest.json`. Same precedent as the `--voice-id` / `--kling-model` flags added 2026-05-16 ([[project_api_automation_plan]] precedent). A separate Claude session in ai-bible-gospels handles that 10-line edit.
- **Effort: ~1 full day**, not half-day. ASS karaoke timing + Windows FFmpeg subtitle-path escaping (colon escapes) eat the time. Python plumbing is trivial.
- **A/B detour worth considering on canary day:** `eleven_turbo_v2` vs `_multilingual_v2` for Daniel voice. If quality holds on Turbo, halves TTS cost (~$2/video more savings).

Related: [[reference_daniel_voice]] (voice ID locked), [[reference_aspect_ratios]] (16:9 + 9:16 both supported day one).
