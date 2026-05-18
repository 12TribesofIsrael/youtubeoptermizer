---
name: custom-script-2-pipeline
description: "Verbatim-preserving Bible-video pipeline that bypasses Custom Script Mode's Claude scene-generator; entry points + flow"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9a9379a4-a54f-4582-892e-f286cf99730c
---

**Custom Script 2.0** is the verbatim-preserving cinematic Bible-video pipeline for the AI Bible Gospels channel. Built 2026-05-17 to bypass Custom Script Mode's Claude scene-generator (which paraphrased 22 of 39 verbatim KJV verses on the first Edom attempt).

## Flow

```
drafts/{topic}-longform-{date}.txt          (authored Format v2 .txt)
    ↓ python scripts/script-to-scenes.py
output/scenes/{topic}-part{1,2}-scenes.json (auto-injected identity stacks)
    ↓ python scripts/render-via-pipeline.py
fal-ai/flux-lora → fal-ai/kling-video → fal-ai/json2video → MP4
```

## Key file locations (`c:/Users/Claude/youtubeoptermizer/`)

| Component | Path |
|---|---|
| Format spec | `docs/script-format-v2.md` |
| Usage guide | `docs/custom-script-2.0.md` |
| Converter | `scripts/script-to-scenes.py` |
| Wrapper | `scripts/render-via-pipeline.py` |
| Patch render | `scripts/render-patch.py` |
| LoRA trainer | `scripts/train-flux-lora.py` |
| fal.ai scraper | `scripts/scrape-fal-history-v2.py` |
| LoRA config | `training/lora-config.json` (gitignored) |
| Training refs | `training/lora-references/{archetype}/` (gitignored) |

## Sibling repo dependency

The pipeline shells out to `C:/Users/Claude/ai-bible-gospels/workflows/custom-script/generate.py` (READ-ONLY repo). Three flags were added there 2026-05-17:
- `--voice-id` (default Daniel `onwK4e9ZLuTAKqWW03F9`)
- `--kling-model` with full v1.6/v2.1/v3.0/v3.0-pro/o3/o3-pro map
- `--lora-url` + `--lora-trigger` + `--lora-scale` routing FLUX to `fal-ai/flux-lora` endpoint

All defaults preserve prior behavior — web UI / other callers untouched.

## LoRA

Trigger word: `aibgospels`. Trained 2026-05-17 on 148 captioned photoreal images (israelite 90 / greek 16 / roman 11 / scene 31), 1500 steps, ~$10. URL stored in `training/lora-config.json` and auto-loaded by the wrapper.

## Hardened rules

See related memories: [[black-hebrew-israelite-phrase-required]], [[esau-edom-caucasian-rule]], [[jacob-blessing-narrative-rule]], [[canonical-identity-framework]], [[visual-block-list]].
