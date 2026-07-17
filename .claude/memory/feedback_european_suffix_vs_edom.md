---
name: feedback_european_suffix_vs_edom
description: "EDOM_SUFFIX hard-codes ancient Edomite garments — use EUROPEAN_SUFFIX for post-biblical Europeans (Blumenbach, Granada 1492)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7ab7509-48d8-4513-bb44-a0c0a9c3c5de
---

`EDOM_SUFFIX` in `scripts/script-to-scenes.py` renders Caucasian **and** forces "ancient Edomite
garments". Correct for Esau/Edom biblical scenes; wrong for any post-biblical European. On the
2026-07-16 Eden→Timbuktu canary it put Johann Blumenbach — an 18th-century German naturalist in
his 1795 study — in a biblical robe.

Added `EUROPEAN_SUFFIX` beside it: same pale-Caucasian lever, "period-accurate dress and setting
for the era described in the scene", no Edomite costume. Not a theological claim about Esau —
purely "render this figure as European."

**Why:** the full-doc pipeline needs Europeans in three eras (1795 study, Granada 1492, northern
migration). One costume-locked suffix can't serve all three.

**How to apply:** biblical Esau/Edom → `EDOM_SUFFIX`. Any other European → `EUROPEAN_SUFFIX`.
Both live ONCE in the converter per [[feedback_canonical_identity_framework]].

Related: [[feedback_esau_edom_caucasian_rule]], [[feedback_black_hebrew_israelite_phrase]]
