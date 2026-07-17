---
name: feedback_card_copy_must_be_literal
description: "Describe a card and gpt-image-1 invents its content — always specify the exact words, and pull scripture verbatim from the 1611 PDF"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7ab7509-48d8-4513-bb44-a0c0a9c3c5de
---

A card prompt that *describes* rather than *specifies* leaves the model nothing to set, so it
invents plausible copy. Every card needs its literal words in the plan.

**Proofs (2026-07-16, Eden→Timbuktu):**
- "the inheritance list building line by line" → rendered **"THE INHERITANCE / A HOUSE / A CAR /
  A CLOCK / A RING / A BIBLE"**. It read "inheritance" as an estate and wrote a will.
- Chapter card copy lived in the plan's header line, not the Visual line; the parser dropped it
  and the card rendered **"MOUNT ARARAT"** instead of "II. The Origin of the Nations". Would have
  hit all 7 chapter cards.
- **The dangerous one:** the Deuteronomy 28:68 card said only "the words of Deuteronomy 28:68
  glowing gold" — with no verse text it would have **fabricated scripture** on a gold card, on a
  scripture channel. Caught before render by auditing all 18 cards.

**How to apply:**
- Audit every CARD for literal copy before a bulk run. If it has none, it *will* invent some.
- Specified copy renders **flawlessly** — the fixed 7-line receipts card is perfect. Capability
  isn't the limit; specification is.
- **Scripture: always `pdftotext docs/1611KjvW_apocrypha*.pdf` and paste verbatim.** Never from
  model memory — that's the standing channel rule and this is exactly the failure it guards.
- Horizontal chains drop items past ~3; stacked lists handle 7 fine.

Related: [[feedback_no_text_suffix_garbles_labels]], [[feedback_gpt_image_1_for_title_cards]],
[[feedback_gpt_image_ancient_glyphs_gibberish]]
