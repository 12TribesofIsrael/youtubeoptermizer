---
name: feedback_never_generate_primary_sources
description: Never let an image generator invent an artifact the narration calls evidence — source the real PD scan; the pipeline now hard-refuses must-source scenes
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7ab7509-48d8-4513-bb44-a0c0a9c3c5de
---

If the narration points at an image and calls it **evidence** ("on the maps the Europeans drew,
there appeared a Black emperor…"), that image must be the **real artifact**. A generated
stand-in is a forged primary source.

**What happened (2026-07-16):** the Eden plan marked p7_7 "genuine PD manuscript — source it, do
not generate it." `generate-eden-full-visuals.py` had no concept of that and silently produced a
convincing fake Catalan Atlas — aged vellum, crowned Black king, gold nugget. It would have
shipped as the historical record. Quarantined to `output/cards/eden-full/_rejected/`.

**Why this is severe, not cosmetic:** the channel lost YPP for **"inauthentic content"**.
Fabricating a 14th-century manuscript while calling it the receipt is the single best gift you
could hand a critic — and it's unnecessary, because the real thing is free.

**The real one is better anyway.** BnF Dépt. des manuscrits, Espagnol 30 — Abraham Cresques,
1375, 3712×2647, public domain. Wikimedia: `Catalan_Atlas_BNF_Sheet_6_Mansa_Musa.jpg`. Its own
Catalan caption calls Mansa Musa *"senyor dels negres de Gineua… el pus noble senyor"* — the
narration's exact claim in a European hand — and the sheet labels Tagaza and Gougou (Gao),
corroborating the salt-trade and Songhay material. Generated art cannot carry that weight,
because the weight is that it's real.

**How to apply:**
- The generator now **hard-refuses** any cue matching `source it, do not generate|genuine PD`.
- Fetch PD scans with `requests` (curl returned http_code=000 on this machine), set a real
  User-Agent, verify the license statement before downloading, and **matte uncropped** onto the
  brand canvas — never crop a primary source to fit a layout.
- Record provenance in the scene plan (institution, accession, date, resolution, license) and
  mark it DO NOT REGENERATE.
- Atmospheric stills that don't claim to be a specific document (a scribe's hand, a library
  interior) are fine generated — the line is whether the narration calls it evidence.

Related: [[reference_eden_full_doc_pipeline]], [[project_ypp_suspension_2026]],
[[project_eden_single_cut_decision]]
