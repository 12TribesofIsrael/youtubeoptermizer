---
name: feedback_no_text_suffix_garbles_labels
description: "SAFETY_SUFFIX's \"no text, no letters\" contradicts any scene needing captions — the model garbles names rather than picking a side"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7ab7509-48d8-4513-bb44-a0c0a9c3c5de
---

`SAFETY_SUFFIX` in `scripts/script-to-scenes.py` ends with ", no text, no letters, no symbols".
That is right for almost every still — but if the *visual cue* also asks for names or labels, the
prompt contradicts itself and gpt-image-1 resolves it by **garbling**, not by choosing.

**Proof (2026-07-16, Eden p4_3 family tree):** cue asked for "Abraham branching to Ishmael and
Isaac"; suffix said no letters. Render printed **ISHMAEL twice, omitted Abraham entirely**, and
mislabelled the tiers. Tommy caught it. Nine scenes doc-wide had the same conflict.

**The fix has two branches:**
- **Decorative text → remove it.** Same rule the maps already use: no written labels, narration
  speaks every name. Applied to the Genesis-10 branches, the Europa trace, the flaring generation
  names, the JUDAH ignite, the "1492" numeral.
- **Load-bearing text → let it win.** Mark the cue `ALLOW TEXT`; the generator then strips the
  ", no text, no letters, no symbols" clause and keeps the photoreal/camera half. Specify copy
  **per element** ("caption directly beneath it: ABRAHAM"), never as description.

**Why it matters:** gpt-image-1 sets specified text *flawlessly* (the 7-line INHERITANCE receipts
card is perfect). Capability was never the problem — the contradiction was.

Related: [[feedback_gpt_image_ancient_glyphs_gibberish]], [[feedback_card_copy_must_be_literal]],
[[reference_eden_full_doc_pipeline]]
