---
name: feedback_kling_generate_audio_defaults_true
description: fal Kling defaults generate_audio=true — omitting it bills +50% for silent tracks; verify the payload matches the quoted rate BEFORE spending
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7ab7509-48d8-4513-bb44-a0c0a9c3c5de
---

**`generate_audio` defaults to `true`** on fal's Kling v3 endpoints. Omit it and every render
bills at the audio-ON rate.

**What it cost (2026-07-16, Eden→Timbuktu figure clips):** the payload carried only `image_url`,
`prompt`, `duration`, `cfg_scale`. "Audio off" existed *only* in code comments and the cost
table — never in the request. Result: pro billed **$2.52/clip instead of $1.68** (+50%). Ten
renders burned **~$26.46** against a **~$14 estimate quoted to Thomas**, leaving $1.39 — not
enough to re-render a single clip if one had needed it. The audio we paid for measured
**-55.9 dB mean** (silence), and narration overwrites it regardless.

**The real lesson is bigger than one flag:** I quoted a price from a rate table while the code
never configured that rate. A comment saying "audio off" is not audio off. **Before any paid
bulk run, assert the payload actually matches the quoted rate** — and prefer measuring spend
against the balance after the FIRST unit, not after all eight.

**How to apply:**
- Always pass `"generate_audio": False` explicitly for documentary B-roll.
- `scripts/render-eden-kling.py` now sets it, with the rate table noted as depending on it.
- Sanity-check: balance delta after clip #1 should match the per-clip quote. If it doesn't, stop.

Related: [[reference_kling_v3_resolution_tiers]], [[feedback_canary_before_bulk]],
[[feedback_elevenlabs_key_scope]]
