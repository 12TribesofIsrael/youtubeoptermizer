---
name: esau-edom-caucasian-rule
description: "Esau, Edom, and Edomites must be rendered as Caucasian/European in AI Bible Gospels content — the theological inverse of the Black Hebrew Israelite rule for Israelites"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9a9379a4-a54f-4582-892e-f286cf99730c
---

For any FLUX/Kling image prompt depicting **Esau, Edom, or Edomites**, render as **Caucasian European with pale/fair complexion, reddish-tinged skin, brown or auburn hair**. This is the THEOLOGICAL INVERSE of the [[black-hebrew-israelite-phrase-required]] rule.

**Why:** The AI Bible Gospels channel is built on a Hebrew Israelite worldview where:
- Jacob → Israel → **Black Hebrew Israelites**
- Esau → Edom → **Caucasian/European peoples**

Genesis 25:25 is the load-bearing verse: "And the first came out red, all over like an hairy garment; and they called his name Esau." The Hebrew word for "red" is the etymological root of "Edom." This is interpreted as the origin of the European bloodline. Without this racial contrast, content like "Why Did Christ Vow to Destroy Edom" theologically collapses — two melanated men sharing pottage doesn't communicate the Jacob-vs-Esau prophecy split that the channel's content depends on.

**Discovered:** 2026-05-16 during the second Edom Part 1 render. After upgrading prompts with the strong "Black Hebrew Israelite" stack (per [[black-hebrew-israelite-phrase-required]]), Tommy flagged that scene 11 (Esau eating pottage from Jacob's bowl) rendered with TWO Black men — wrong. Esau was getting the Israelite injection.

**How to apply:**
- The converter at [scripts/script-to-scenes.py](../../../../../../c:/Users/Claude/youtubeoptermizer/scripts/script-to-scenes.py) detects mentions of Esau / Edom / Edomite / Edomites in the `[Visual:]` prompt and appends `EDOM_SUFFIX` (Caucasian European stack) INSTEAD of `MELANATED_SUFFIX`. Do not weaken or remove this branch.
- For **mixed-brothers scenes** (Jacob AND Esau in the same frame — pottage moment, Isaac's blessing): the converter does NOT auto-inject either suffix to avoid contradictions. Source `[Visual:]` cue MUST explicitly describe both: "Black Hebrew Israelite Jacob seated calmly while pale Caucasian Esau leans over the bowl." The converter logs these as `MIXED-BROTHERS` for manual verification.
- **Edomite warriors / refugees / stonemasons** in Obadiah/Malachi scenes (Part 2 of Edom video): all Caucasian. The converter handles this automatically via the `EDOM_INDICATORS` check.
- **Isaac, Rebekah, Jacob himself** are Israelites → Black per the [[black-hebrew-israelite-phrase-required]] rule. Only Esau and his descendants flip to Caucasian.
- Scenes where **Jacob disguises himself as Esau** (goat-skins on smooth arms while approaching blind Isaac) — Jacob's actual skin stays Black; the goat-skins are a costume. Source cue should say "Jacob wearing goat-skins on his smooth dark-brown arms" — converter correctly auto-injects Black Hebrew Israelite stack since "Esau" isn't the named subject.
- **Newborn-twins exception (Genesis 25:25):** at birth, BOTH babies are rendered as melanated Black. Esau's "red and hairy garment" detail comes through via **auburn / reddish curly hair**, NOT Caucasian skin. The full racial inversion only kicks in for ADULT Esau scenes (despising the birthright + onward). Validated 2026-05-17 — Tommy confirmed the original "both dark-brown-skinned, melanated" prompt rendered correctly when paired with "red and hairy like a garment" on Esau's hair.

**Burn cost from this discovery:** part of the second ~$30 fal.ai Part 1 render — 5 scenes (7, 8, 10, 11, 16) need surgical regeneration via the web UI's Fix a Scene panel (~$1.20 total). The converter is now wired correctly so Part 2 of Edom (which has burning-city Edomite refugees + Edomite stonemasons + warriors) won't repeat the mistake.

Related: [[black-hebrew-israelite-phrase-required]] (Israelite rule), CLAUDE.md "Character Depiction Rule" (currently only specifies the Israelite half — should be expanded), `docs/custom-script-2.0.md`.
