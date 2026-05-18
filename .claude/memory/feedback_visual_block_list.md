---
name: visual-block-list
description: Permanent block list of visual-cue patterns that produce inappropriate renders — converter HARD-FAILS on any of these
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9a9379a4-a54f-4582-892e-f286cf99730c
---

The following visual-cue patterns are **PERMANENTLY BLOCKED** from any AI Bible Gospels script. The converter at [scripts/script-to-scenes.py](../../../../../../c:/Users/Claude/youtubeoptermizer/scripts/script-to-scenes.py) raises `ValueError` on any source `.txt` that contains them — conversion fails until the source is rewritten.

**Blocked patterns (case-insensitive, word-boundary match):**
- `embracing`, `embrace`, `embraced`
- `kissing`, `kiss`, `kissed`
- `intimate contact`, `intimately`
- `face-to-face`, `face to face`
- `lips touching`, `lips meeting`
- `romantic`, `romantically`
- `lovers`

**Why:** On 2026-05-17 the Edom Part 2 video rendered a scene captioned "Jacob and Joseph reunited — two melanated dark-brown-skinned figures embracing in golden divine light at the top of a mountain." FLUX produced an image of two bearded men face-to-face in what visually reads as a romantic kiss — a brand-killing render for a Hebrew Israelite Bible channel. Tommy flagged it immediately and emphasized: **"especially two men."**

**The cardinal rule — TWO MALE FIGURES MUST NEVER appear in any close-quarters physical pose that could read as romantic, intimate, or homoerotic.** This is the absolute hard line and supersedes biblical-accuracy arguments. Bible scenes that traditionally depict male-male reunions (Jacob+Esau in Gen 33:4, Joseph+his brothers in Gen 45, David+Jonathan, etc.) MUST be rendered with one of the safer alternatives listed below — never face-to-face, never embracing, never with arms wrapped around each other, never with faces in proximity.

**From this point forward: NO render of two male figures in physical close-quarters contact, regardless of biblical context (reunions, brotherhood, prophet greetings, father-son moments, etc.). This is non-negotiable for the channel's Hebrew Israelite audience and brand.**

**Safer alternatives for "reunion / together" framings:**
- Solo dignified figure on mountaintop, arms raised in praise, back to camera, gazing at horizon
- Two figures **standing side by side, facing the horizon** (NOT facing each other)
- Father seated + son **kneeling at his feet** receiving blessing (hierarchical, not face-to-face)
- Group of multiple figures (3+) in formation looking outward at sunset
- Hand on shoulder from BEHIND (not from front)
- Patriarch placing hand on TOP of bowed head

**Acceptable physical contact patterns (per existing channel content):**
- Hand placed on bowed head (blessing — biblical, hierarchical)
- One figure kneeling at another's feet (subservient pose — biblical, non-intimate)
- Hand on a scroll / object held between two figures
- One figure resting hand on another's shoulder from behind

**How to apply:**
- When writing or editing any `[Visual:]` cue, NEVER use blocked words. Reach for the safer alternatives above.
- The converter enforces this at parse time. If you (or future Claude) tries to render a script with these patterns, the converter fails loudly with `Scene at line X: visual cue contains BLOCKED pattern 'embracing'`.
- This rule supersedes any "biblical accuracy" argument — even reunions described in scripture (Jacob+Esau in Gen 33:4, Joseph+brothers in Gen 45) must be rendered with one of the safer alternatives.

**Existing rendered scenes that violated this rule:**
- Edom Part 2 final video (rendered 2026-05-17): scene 21 (Jacob+Joseph reunited) — the offending render. The source `.txt` has been fixed but the existing Part 2 MP4 still contains the bad render. Will be replaced when Tommy re-renders via Custom Script Mode + v3.0 himself.

Related: [[esau-edom-caucasian-rule]] (theology), [[canonical-identity-framework]] (visual stack), [[jacob-blessing-narrative-rule]] (narration framing).
