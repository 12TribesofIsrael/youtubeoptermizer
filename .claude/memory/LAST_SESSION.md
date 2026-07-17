---
name: ""
metadata: 
  node_type: memory
  ended: 2026-07-17T00:15:00-04:00
  project: youtubeoptermizer (AI Bible Gospels)
  branch: main
  originSessionId: f7ab7509-48d8-4513-bb44-a0c0a9c3c5de
---

# Last Session — 2026-07-16

## What the user wanted
Started as "what's next on our list" — became a full strategic re-plan plus the entire visual
build of the flagship documentary. Tommy wanted the highest-leverage next move; the analytics
said the 8-part drip couldn't work, so we pivoted to one 86-min cut and built all 103 scenes.

## What we did
- **Diagnosed the real YPP blocker** (this reframes everything — see
  [[project_eden_single_cut_decision]]): reapply is greyed out on **eligibility, not date** —
  1,393/3,000 valid public watch hrs. YPP watch hours **exclude Shorts** (Shorts path is 3M
  views/90d; channel did 72K in a *year*). ONE video — "The Prophecy Revealed" (1h29m,
  `mAJS97kNC5E`) — carries ~1,100 of 1,389 qualifying hrs, stable/growing, ~100-150 hrs/mo.
- **Verified Part 1 shipped**: `vnkEWbCVMTA` went PUBLIC 2026-07-03 (47 views/2wks). Channel:
  6,000 subs, 740,810 views, 211 videos, monetization off.
- **Pivoted to a single ~86-min cut.** Watch hrs = duration x views; a 13.6-min part can't be an
  engine at any retention. 86 min ≈ Prophecy Revealed's 89. Realistic approval: **2027**.
- **Recovered Part 1's assets from the laptop** — mapped `Z:` → `\\10.0.0.82\repos` persistently
  (`net use /persistent:yes`; creds were already saved). All 6 Kling clips + 110 files / 579 MB
  copied to the desktop and verified (size match + decode probe).
- **Found the 86.2-min ElevenLabs narration** already on disk — verified complete by Whispering
  the last 45s (ends on the exact sign-off). Independently confirmed by word count: 12,873 words
  (Parts 2-8) ≈ 73.6 min + Part One's ~12 = ~86.
- **Wrote + built the whole thing** (commit `df49e08`): 103-scene plan, parser, generator,
  scripture typesetter, Kling runner. **95 stills/cards + 8 Kling clips @1920x1080/15s.**
- Spend: ~$18 OpenAI, ~$26 fal (~$44 total). **fal balance now $1.39.**

## Decisions worth remembering
- **Density**: ~42s/scene (103 scenes), not Part One's 31s churn. I overshot my own ~60s
  recommendation and said so; Tommy accepted 42s.
- **Kling audio OFF + pro tier**: pro is the only 1080p path (standard caps at 720p) — must match
  Part One's six 1080p clips. See [[reference_kling_v3_resolution_tiers]].
- **Catalan Atlas sourced, not generated** — see [[feedback_never_generate_primary_sources]].
- **Part One stays public as a teaser/funnel** into the full cut (deferred to launch day).

## Open threads / next session starts here
1. **TOP UP FAL — $1.39 left.** No room to re-render even one clip. Suggest ~$20.
2. **Narration**: regenerate per-scene TTS from the plan (voice `RKqAcMj3TkzJjyZpEbj0`, speed
   0.92). Part One's 26 scenes are TTS-cached and won't re-cost. The 86-min mp3 is the runtime
   *reference*, not the build source. **This was approved but not yet started.**
3. **Assemble** via `scripts/assemble-video.py`; Part One reuses `output/*/eden-part1*`.
4. **SFX still untested** — the 13-file library exists but `tag-sfx.py` has never run against a
   real manifest (open since 2026-06-17).
5. Optional: the p3_6 chain card renders 3 of 4 words (drops "ENGLISH") — Tommy waved it through.
6. Long-cold (from the stale 06-17 log): `--assemble` flag on `render-via-pipeline.py`, Modal
   deployment, Whisper `small.en`.

## Uncommitted work
Clean working tree. `df49e08` pushed to origin.

## Note on process
Every failure this build had ONE root cause: **description leaking into copy, or prohibitions
naming what they forbade**. Chapter card printed "MOUNT ARARAT"; receipts card invented "A HOUSE
/ A CAR / A CLOCK"; family tree printed ISHMAEL twice with no Abraham (Tommy caught it); "do not
depict the prophet Mohammed" rendered a robed man at the Kaaba; CTA grew a "THE SUNRISE
CONTINUES" headline. Canaries caught nearly all of it — 4 images before 95, 1 Kling clip before
8. **Keep the canary discipline.**

Also: a memory file I'd confirmed written silently vanished mid-session
(`reference_kling_v3_resolution_tiers.md`) — only caught because the MEMORY.md index count
didn't move. Verify the count, don't trust "file created".
