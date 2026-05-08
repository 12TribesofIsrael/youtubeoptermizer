---
name: Remotion video framework
description: Reusable pattern for branded video production via Remotion — anchor doc proven 2026-05-07, applies to every future video on the channel
type: reference
originSessionId: 0734df78-6a4b-4eea-9432-c912278f58f1
---
`docs/remotion-video-framework.md` is the canonical playbook for any video work on this channel that's bigger than a one-off social Short.

**Reference implementation:** `src/anchor-doc/` — the Faith Walk Live anchor documentary (13:10 long-form). Copy this folder as the starting point for every new video; swap the inputs in `public/{audio,clips,cards}/` and edit `src/timeline.ts`.

**Scaffolding already in place:**
- `scripts/transcribe-narrations.py` — Whisper batch transcription with timeline-offset cues → `subtitles.json`
- `scripts/generate-title-cards.py` — gpt-image-1 brand card generation (gold-on-black)
- `scripts/generate-narration.py` — ElevenLabs Daniel voice TTS
- Skills: `create-highlight-reel`, `create-reel`, `pan-3d-transition`, `add-covers`

**The framework solves:**
- ~3 hours upfront cost vs 4-6 hours per CapCut/Canva cut
- Re-renders in ~30-50 min instead of re-editing
- Brand consistency via `theme.ts` carried across videos
- Deterministic subtitle pipeline via Whisper → JSON
- Re-runnable builds from git source

**The framework does NOT solve:** pro color grade (use DaVinci/CapCut for final pass), audio ducking under voice (finish in Canva), AI video generation (use Kling, then drop into Remotion).

**When to use:** 10+ min long-form, scripted with multiple clips + cards + narration, likely to iterate. **When NOT to use:** single-clip videos, one-off Shorts, anything you'd edit once and ship.

Future videos sized for this framework: Faith Walk Live recaps (Day 100, halfway, arrival), Phase 4B Bible explainers, Deuteronomy 28 series.
