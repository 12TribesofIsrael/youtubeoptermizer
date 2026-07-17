---
name: feedback_negative_pose_prompts_backfire
description: "Never write \"no embrace / no face-to-face\" in a visual cue — the blocked-pose gate fails it AND diffusion models latch onto the forbidden word"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f7ab7509-48d8-4513-bb44-a0c0a9c3c5de
---

Writing a blocked pose as a **negative instruction** ("no contact, no embrace, no face-to-face
intimacy") is wrong twice over:

1. `BLOCKED_RE` in `scripts/script-to-scenes.py` matches the *word*, not the intent — so the cue
   hard-fails conversion regardless of the "no".
2. More importantly, diffusion models handle negation poorly and frequently render the very thing
   being forbidden. "No embrace" is a good way to get an embrace.

**Why:** hit on 2026-07-16 writing the Eden→Timbuktu full-doc scene plan — three scenes (Joseph
and his brothers, Sheba/Solomon, Jacob's Genesis 49 blessing) all failed the gate on my own cue.

**How to apply:** describe the desired spacing **positively and physically** instead. "A wide
empty span of polished floor separating the throne from the kneeling men, each figure isolated in
his own space" — not "no embrace". Same for "halting at the threshold", "kneeling in a wide arc
several paces back".

Related: [[feedback_visual_block_list]], [[feedback_canonical_identity_framework]]
