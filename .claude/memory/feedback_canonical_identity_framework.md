---
name: canonical-identity-framework
description: "The converter at scripts/script-to-scenes.py is the FRAMEWORK — canonical identity language for every archetype lives there and ALWAYS injects (additive reinforcement), not in individual source visual cues"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9a9379a4-a54f-4582-892e-f286cf99730c
---

The canonical identity stacks for the AI Bible Gospels visual archetypes live in **one place — the converter at [scripts/script-to-scenes.py](../../../../../../c:/Users/Claude/youtubeoptermizer/scripts/script-to-scenes.py)** — and **ALWAYS** inject on every matching scene, regardless of whether the source `[Visual:]` cue already contains identity language. The redundancy is intentional — repeated emphasis reinforces FLUX's identity signal.

**Three canonical stacks (locked 2026-05-17 per Tommy):**

1. **`MELANATED_SUFFIX`** (heavy/adult Israelite): `", Black Hebrew Israelite with rich African American complexion, deeply melanated dark brown skin, natural afro-textured hair in locs, braids, or twists, wearing earth-toned Hebrew robes with tzitzit fringes"`
   - Used on adult-male Israelite scenes (prophets, patriarchs, warriors, kings).
   - Avoided on babies/women/children because `"locs/braids/full beard/tzitzit"` overrides scene-specific markers like "red hair" or "head wrap" (proven on 2026-05-17 newborn-twins render — heavy stack erased Esau's auburn-hair detail).

2. **`LIGHT_MELANATED_SUFFIX`** (light/non-adult Israelite): `", Black Hebrew Israelite with rich African American complexion, deeply melanated dark brown skin"`
   - Used on baby/woman/child/mother scenes detected via `LIGHT_IDENTITY_TRIGGERS` (newborn, baby, infant, child, woman, mother, pregnant, womb, Rebekah, Sarah, Hagar, Miriam, Hannah, Mary, etc.).
   - Same identity assertion + complexion + skin, no over-specified secondary descriptors.

3. **`EDOM_SUFFIX`** (Caucasian Edomite — the theological inverse): `", Caucasian European with pale fair complexion, reddish-tinged skin, hairy, brown or auburn hair and beard, ancient Edomite garments, NOT African, NOT melanated, NOT Black Hebrew Israelite"`
   - Used on scenes mentioning Esau / Edom / Edomite / Edomites (per [[esau-edom-caucasian-rule]]).

**The framework rule:**
- **Don't** put identity language into individual `[Visual:]` cues in the source `.txt` and rely on it being consistent — it never is (some scenes have full identity, others don't, FLUX renders inconsistently).
- **DO** put scene-specific content (composition, pose, action, lighting, setting) in the `[Visual:]` cue, and let the converter inject the canonical identity stack automatically on every scene.
- The converter's `build_scene_dict()` triggers ALWAYS now (no `not has_strong_identity` guard) — was changed 2026-05-17 because the previous skip-if-present logic caused inconsistent stacking across scenes.

**Light vs heavy path detection:**
The converter regex `LIGHT_IDENTITY_RE` triggers the lighter path on any scene mentioning: newborn / baby / infant / child / woman / mother / wife / girl / daughter / pregnant / womb / fetus + named biblical women (Rebekah, Sarah, Hagar, Miriam, Hannah, Mary, Ruth, Esther, Tamar, Deborah, Rachel, Leah). All other Israelite scenes get the heavy adult-male path.

**When updating the canonical stacks:**
- Edit the constants at the top of `scripts/script-to-scenes.py` (search for `MELANATED_SUFFIX`, `LIGHT_MELANATED_SUFFIX`, `EDOM_SUFFIX`).
- Re-run the converter to regenerate `output/scenes/*.json`.
- Optionally re-render scenes that need the updated identity — but ONLY if FLUX renders are visually worse than the previous stack. The cost-prudent default is to leave already-rendered Kling clips alone and apply the new stack only to fresh scenes.

**Discovered:** 2026-05-17. Tommy noticed that "deeply melanated dark-brown-skinned man Isaac with rich African American complexion" only appeared in some prompts, not all Israelite scenes — flagged the inconsistency. The fix moves all identity language into the converter as ALWAYS-inject canonical stacks.

Related: [[black-hebrew-israelite-phrase-required]], [[esau-edom-caucasian-rule]], [[jacob-blessing-narrative-rule]], [docs/custom-script-2.0.md](../../../../../../c:/Users/Claude/youtubeoptermizer/docs/custom-script-2.0.md).
