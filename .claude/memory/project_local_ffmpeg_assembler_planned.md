---
name: local-ffmpeg-assembler-built
description: Local FFmpeg assembler replacing JSON2Video — BUILT and validated 2026-05-27; live in scripts/assemble-video.py; subtitle timing fixed; Modal deployment next
metadata: 
  node_type: memory
  type: project
  originSessionId: 51b1b09d-2943-411c-a6ef-5b536434ea27
---

A local FFmpeg-based video assembler that replaces JSON2Video as the last-mile step in the Custom Script 2.0 pipeline. Ingests a `clips_manifest.json` → downloads Kling clips → ElevenLabs TTS → Whisper word timestamps → FFmpeg Pass A (per-scene loop+mux) → FFmpeg Pass B (concat + burn ASS karaoke subs) → branded MP4.

**Status as of 2026-05-27:** BUILT and validated. 1-scene canary ✅, 3-scene boundary ✅, 19-scene full render (1 Maccabees Ch.3, 512 MB) ✅. Committed at e36f1b8. Entry point: `scripts/assemble-video.py`.

**Critical bug fixed 2026-05-27:** Subtitle timing drift — raw MP3 durations were used for cumulative ASS offsets, but each Pass A scene is ~2.4s longer than the raw audio (FFmpeg 8.x buffer overhead with `-stream_loop -1 -shortest -fflags +genpts`). Fix: write merged ASS AFTER Pass A, probe Pass A output durations. See [[feedback_ffmpeg_pass_a_duration_overshoot]].

**Integration:** Two-step right now — `render-via-pipeline.py --skip-json2video` writes manifest, then `assemble-video.py --manifest <path>`. Open: wire `--assemble` flag on render-via-pipeline.py to chain them automatically (~10 lines).

**Why:** Saves ~$1-2/video vs JSON2Video ($0 for FFmpeg assembly). Bigger win: no external render dependency. Designed as the rendering core for a future hosted product on aibiblegospels.com. See [[project_ffmpeg_assembler_saas_intent]].

**How to apply:**
- Run: `python scripts/assemble-video.py --manifest tests/fixtures/maccabees_ch3_manifest.json`
- Canary: add `--scenes 3 --keep-intermediates` to test without full API spend
- Whisper upgrade: `--whisper-model small.en` for better KJV proper-noun timing
- Intermediates are file-cached — re-runs skip TTS/download/Pass A if files exist

Related: [[reference_daniel_voice]], [[project_ffmpeg_assembler_saas_intent]], [[feedback_ffmpeg_pass_a_duration_overshoot]].
