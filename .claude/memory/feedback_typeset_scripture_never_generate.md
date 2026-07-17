---
name: feedback_typeset_scripture_never_generate
description: Never let gpt-image-1 render scripture — it drops and misspells words while looking authoritative; typeset with PIL over a text-free background
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7ab7509-48d8-4513-bb44-a0c0a9c3c5de
---

**gpt-image-1 cannot be trusted with scripture.** It fails in a uniquely dangerous way: the
output *looks* authoritative — gold serif on black reads as scripture whether or not the words
are right — so errors survive review unless someone reads every word against the source.

**Proof — Deut 28:68 card, Eden→Timbuktu, 2026-07-16, three consecutive attempts:**
1. Full 47-word verse → silently **dropped "and bondwomen"**, added a comma the KJV lacks, never
   closed the quote. A truncated verse is a falsified verse — in a passage *about* bondmen and
   bondwomen.
2. Elided ~30-word verse → "enemiess", "DEUTERONOMMY".
3. Retry → "ERING" for "BRING", "DEUTERONOMMY" **again**. Systematic, not unlucky.

Shortening the text did not fix it. Retrying did not fix it.

**The fix — `scripts/compose-scripture-card.py`:** the model renders only the LIGHT (background,
book/scroll, negative space — prompt it for blank pages and "no legible script"); **Python renders
the WORDS** with PIL over it. Constantia (`C:/Windows/Fonts/constan.ttf`) at ~62px, gold
(232,183,90), gaussian-blur glow passes, letter-spaced bold reference line. Typeset text is
correct by construction.

**How to apply:**
- ANY card carrying scripture → typeset. Never model-rendered. No exceptions.
- Verse text pasted verbatim from `docs/1611KjvW_apocrypha - Copy.pdf` via pdftotext.
- Short brand cards (chapter titles, `ALEPH · BETH → ALPHABET`, the 7-line INHERITANCE list)
  DO render fine from the model — the limit is length + stakes, and scripture is max stakes.

Related: [[feedback_card_copy_must_be_literal]], [[feedback_gpt_image_1_for_title_cards]],
[[feedback_gpt_image_ancient_glyphs_gibberish]], [[reference_eden_full_doc_pipeline]]
