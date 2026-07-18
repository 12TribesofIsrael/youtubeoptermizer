---
name: reference_viral_thumbnail_generator
description: "scripts/generate-eden-full-thumbnail.py — viral 1280x720 thumbnails via fal FLUX-pro background + PIL gold-serif typeset text (reliable, no garbled letters)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: e880ab15-018e-4a34-98c6-9e572112c856
---

`scripts/generate-eden-full-thumbnail.py` is the repo's viral-thumbnail generator.
Two-stage, correct-text-by-construction pattern:
1. **fal FLUX-pro** (`https://fal.run/fal-ai/flux-pro/v1.1`, `image_size {width:1280,height:720}`)
   renders ONLY the image — melanated Black Hebrew Israelite figure + golden chiaroscuro +
   deliberate dark negative space. Prompt carries the full identity stack ("NOT white/pale/
   light-skinned, no Caucasian features") and `no text/letters/words`. FAL_KEY read from this
   repo's `.env` or the sibling `../ai-bible-gospels/.env`.
2. **PIL** typesets the title: Constantia Bold (`C:/Windows/Fonts/constanb.ttf`) gold fill +
   dark stroke (`stroke_width`/`stroke_fill`) + GaussianBlur glow, over a side/bottom scrim.

Why: FLUX/gpt-image garble on-image text (same reason as [[typeset_scripture_never_generate]]).
Model renders the LIGHT, Python renders the WORDS. ~$0.05/call on fal.

3 CTR variants written to `output/thumbnails/eden-full/`: `01_hebrews` (regal king, identity
flag), `02_erased` ("THE HISTORY THEY ERASED", close-up direct gaze — highest expected CTR),
`03_origin` (epic wide, "FROM EDEN TO TIMBUKTU"). Run: `python scripts/generate-eden-full-thumbnail.py [variant]`.
Reuse this script for future thumbnails — edit the VARIANTS dict. Relates to [[feedback_black_hebrew_israelite_phrase]].
