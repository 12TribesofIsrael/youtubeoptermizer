---
name: reference_eden_full_doc_pipeline
description: Eden→Timbuktu FULL 86-min doc pipeline — scene plan → parse-scene-plan.py → generate-eden-full-visuals.py → assembler
metadata: 
  node_type: memory
  type: reference
  originSessionId: f7ab7509-48d8-4513-bb44-a0c0a9c3c5de
---

The single-cut ~86-min "From Eden to Timbuktu" documentary (decided 2026-07-16 over the 8-part
drip — see [[project_eden_single_cut_decision]]).

**Chain:**
1. `drafts/eden-full-doc-scene-plan.md` — human source of truth, 103 scenes (Parts Two–Eight +
   Conclusion + CTA). Part One's 26 scenes already built; do NOT regenerate.
2. `scripts/parse-scene-plan.py` → `output/manifests/eden-full-scenes.json`. Resolves each
   scene's `identity` EXPLICITLY (melanated / light / european / none) and hard-fails on blocked
   poses. Run with `--check` to validate without writing.
3. `scripts/generate-eden-full-visuals.py` — gpt-image-1, 1536x1024 quality=high.
   `--canary` (4 proof scenes) · `--all --limit 10` (batches) · `--ids a,b --redo` (targeted).
   Skips existing PNGs by default, so batches are resume-safe and never re-pay.
   Output: `output/cards/eden-full/<id>.png`
4. Kling v3 standard **image-to-video**, 15s, ~$1.26–1.89/clip via fal — needs a gpt-image-1
   still first, so OpenAI quota gates Kling too.

**Identity:** suffixes are imported from `scripts/script-to-scenes.py` (the canonical framework),
never re-declared. See [[feedback_canonical_identity_framework]] and
[[feedback_european_suffix_vs_edom]].

**Part One assets** recovered from the laptop 2026-07-16 and now on the desktop at
`output/{clips,cards,stills,audio}/eden-part1*` — includes all 6 Kling figure clips. Gitignored;
exists on both machines only.

**Narration:** `docs/audio/ElevenLabs_..._Copy.mp3` is a complete 86.2-min single-file read (tail
verified). The assembler wants per-scene audio, so the plan regenerates per-scene TTS; that mp3
is the runtime reference, not the build source.
