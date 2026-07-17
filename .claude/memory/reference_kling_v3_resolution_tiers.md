---
name: reference_kling_v3_resolution_tiers
description: Kling v3 standard caps at 720p and mirrors input aspect — use PRO + a 16:9 1920x1080 source still to get 1080p
metadata: 
  node_type: memory
  type: reference
  originSessionId: f7ab7509-48d8-4513-bb44-a0c0a9c3c5de
---

Measured on fal 2026-07-16 building the Eden→Timbuktu figure clips (15s, image-to-video).

**Two independent things control output resolution:**

1. **Input aspect — Kling mirrors it.**
   - gpt-image-1 native 1536x1024 (3:2) in → **1176x784** out
   - cropped/upscaled 1920x1080 (16:9) in → **1280x720** out
2. **Tier — standard caps at 720p regardless of input.**
   - `v3/standard/image-to-video` + 16:9 in → **1280x720**
   - `v3/pro/image-to-video` + 16:9 in → **1920x1080** ✅

**Part One's six figure clips are all 1920x1080.** Rendering new clips on standard would drop
visibly soft shots into the same documentary beside them. Always match existing footage — and
the only reason this was caught is that Part One existed to compare against.

**Pricing (audio off / audio on) — and see [[feedback_kling_generate_audio_defaults_true]],
`generate_audio` DEFAULTS TO TRUE and must be passed explicitly:**
- standard: $0.084 / $0.126 per sec → 15s = $1.26 / $1.89
- pro:      $0.112 / $0.168 per sec → 15s = **$1.68** / $2.52

**Recipe:** centre-crop the 3:2 still to 16:9, upscale to 1920x1080 (LANCZOS), upload via
`fal_client.upload_file`, render on **pro** with `generate_audio: False`. Cropping is free in
practice — the finished doc is 16:9, so the assembler crops a 3:2 still anyway. Implemented as
`prep_16x9()` in `scripts/render-eden-kling.py`.

**Motion prompts describe the CAMERA, not the subject** — identity/content already live in the
source still; re-describing figures gives Kling a second chance to drift. And the still is
frame 1: don't ask an already-standing crowd to "rise to their feet" — it can't.

Related: [[reference_eden_full_doc_pipeline]], [[feedback_kling_generate_audio_defaults_true]]
