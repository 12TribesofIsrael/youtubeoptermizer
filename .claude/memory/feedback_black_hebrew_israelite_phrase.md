---
name: black-hebrew-israelite-phrase-required
description: "FLUX/Kling prompts for Israelite characters MUST include the literal phrase \"Black Hebrew Israelite\" — weak language like \"dark-brown skinned\" or \"melanated\" alone renders Caucasian"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9a9379a4-a54f-4582-892e-f286cf99730c
---

For any FLUX/Kling image prompt depicting an Israelite/Hebrew biblical figure (Jacob, Esau, Isaac, Christ, prophets, kings, generic Israelites), the **literal phrase "Black Hebrew Israelite"** must appear in the prompt. Backstop with: `"deeply melanated rich dark brown skin"`, `"natural afro-textured hair in locs or braids"`, `"tzitzit fringes"`, and the camera spec `"shot on RED V-Raptor, hyper-detailed skin texture and fabric weave, natural film grain"`.

**Why:** On 2026-05-16 we rendered Edom Part 1 (16 scenes, o3-pro, ~$30 fal.ai burn) using prompts like *"A dark-brown-skinned, melanated elderly Hebrew patriarch... twelve melanated dark-brown sons standing in shadowed amber light. Wool-textured beards and hair. NO Caucasian features."* The output rendered **Caucasian/Mediterranean men** around the deathbed despite explicit "dark-brown, melanated, NO Caucasian" tagging. Negative prompts (`NOT white, NOT pale, NOT Caucasian`) did NOT prevent the drift. Only the **positive identity phrase** `"Black Hebrew Israelite"` reliably steers FLUX. Tommy confirmed via reference prompts that this phrase + `locs` + `tzitzit fringes` + RED V-Raptor camera spec is the proven-working stack.

**How to apply:**
- The converter at [scripts/script-to-scenes.py](../../../../../../c:/Users/Claude/youtubeoptermizer/scripts/script-to-scenes.py) (`MELANATED_SUFFIX` constant) auto-appends the strong stack to any prompt that contains person indicators and lacks the "Black Hebrew Israelite" phrase. Don't weaken or remove this.
- When writing new `[Visual:]` cues in Script Format v2 (`docs/script-format-v2.md`), include `"Black Hebrew Israelite"` directly in the source text rather than relying solely on the auto-injection. The .txt is more readable that way and the converter just no-ops.
- Project-level `CLAUDE.md` "Character Depiction Rule (MANDATORY)" still says `"dark-brown to deep-brown skinned"` / `"wool-textured / coiled / tightly curled hair"` / `"NO Caucasian"` — that language is *insufficient* for FLUX/Kling per this incident. If updating that file, replace with the Black Hebrew Israelite stack. Until then, treat the CLAUDE.md text as a minimum, not a complete spec.
- The `ai-bible-gospels` repo's `SCENE_GENERATION_PROMPT` at `workflows/custom-script/generate.py:43-58` already uses `"Black Hebrew Israelites with rich, deeply melanated dark skin. Natural Afro-textured hair: locs, braids, twists, afros, or traditional head wraps. Traditional Hebrew robes, garments with tzitzit fringes"` — that's the canonical pattern. Mirror it.

**Burn cost from the failure:** ~$30 in fal.ai charges for 16 FLUX + Kling o3-pro scenes that all rendered with wrong race. JSON2Video quota also hit at assembly. Both re-burned after the prompt fix. Don't repeat — verify the strong identity stack appears in every human-figure prompt before firing any render >$5.

Related: [[melanated-character-rule-locked]] (if exists), CLAUDE.md "Character Depiction Rule (MANDATORY)" section, `docs/custom-script-2.0.md`.
