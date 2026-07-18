---
name: project_openai_image_billing_capped
description: OpenAI image account hit billing hard limit 2026-07-17; gpt-image-1 blocked until raised; fal FLUX-pro is the stills fallback
metadata: 
  node_type: memory
  type: project
  originSessionId: 81f136bc-88c3-49b3-8591-4e4864024cc7
---

On 2026-07-17 the OpenAI account's **billing hard limit** was reached mid-session.
`gpt-image-1` calls (both `/images/generations` and `/images/edits`) return
HTTP 400 `billing_hard_limit_reached`. A few image ops earlier in the session had
already succeeded before the cap hit.

**How to apply:** if a gpt-image-1 call 400s with `billing_hard_limit_reached`,
don't send Thomas to fix billing mid-task — route around it with **fal FLUX-pro**
(`https://fal.run/fal-ai/flux-pro`, `image_size: landscape_16_9`, FAL_KEY from
`.env` or `../ai-bible-gospels/.env`). Part One's figure stills were FLUX, so it's
on-brand. Only flag the cap as a follow-up: raising it is a manual step in OpenAI
billing settings that only Thomas can do. Kling stills prep crops to 16:9 anyway.
Related: [[reference_eden_full_doc_pipeline]], [[reference_custom_script_2_pipeline]].
