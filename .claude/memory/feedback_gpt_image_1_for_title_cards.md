---
name: gpt-image-1 nails brand title cards on first pass
description: For gold-on-black AI Bible Gospels brand title cards (incl. multi-line scripture quotes + 6-label CTA stacks), gpt-image-1 renders text correctly first try; DALL-E 3 fallback unnecessary
type: feedback
originSessionId: 22dbbefd-de40-46eb-b5d9-138852773417
---
For the channel's locked brand identity (deep navy-black + gold serif + sparse golden particles + cinematic chiaroscuro), `gpt-image-1` at `quality=high`, `size=1536x1024` produces clean text rendering on the first attempt — including:

- Two-line title cards with Unicode em-dash (`PHILADELPHIA — CALIFORNIA`)
- Multi-line italicized KJV scripture quotes with citation + horizontal divider line (James 1:27, Matthew 25:40)
- 6-label stacked CTA cards with horizontal dividers (TRACK / DONATE / SUBSCRIBE + 3 subtitle lines)

**Why:** gpt-image-1's text rendering is materially better than DALL-E 3 for documentary-style typography. In the 2026-05-06 anchor-doc batch, all 4 cards rendered cleanly first try — no `dall-e-3` fallback was needed.

**How to apply:**
- For this channel's title cards, default to `gpt-image-1` quality=high. Keep `dall-e-3` as a fallback in the script (`scripts/generate-title-cards.py`) but expect first-pass success.
- Cost: ~$0.10/card at high quality, ~$0.40 for the 4-card anchor doc set.
- Aspect note: 1536x1024 is 1.5:1 (slightly squarer than 16:9). For YT 1920x1080, scale-to-height in CapCut and accept a thin pillarbox, or upscale 1.17× to fit width. Don't crop — the text composition is centered.
- Brand-identity prompt prefix in the generator script (BRAND constant) is what locks the gold-on-black aesthetic; keep it consistent across new cards added to the channel.
