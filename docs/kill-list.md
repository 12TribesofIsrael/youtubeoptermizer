# Catalog Cull — Proposed Unlist List

**Drafted:** 2026-04-24
**Target reapply date:** 2026-07-08 (YPP 90-day window opens)
**Action:** DELETE (permanent) — chosen over unlist because YPP reviewers see internal upload history, not just public feed
**Total proposed:** 23 Shorts
**Status:** APPROVED 2026-04-24 — execution pending

## Why these 23

YouTube's rejection cited three specific patterns:
1. "Template across multiple videos"
2. "Minimal variation"
3. "Slideshow with low narrative, commentary, or educational value"

The 23 below are the surviving tail from Phase 1 cleanup that still match those patterns. Each either: (a) sits in a near-duplicate cluster with a clear top performer already earning the views, or (b) is old + low-view enough that it adds nothing to the channel but classifier surface area.

---

## Tier A — Dead weight (15 videos) — DELETE

**Criteria:** Shorts, 90+ days old, under 200 views. No debate — nothing is being surfaced, and the title patterns match the flag.

| Views | Age | Video ID | Title |
|---:|---:|---|---|
| 37 | 221d | `3riiNCfzQ_g` | They've Been Using the Same Deception for 2000 Years |
| 58 | 218d | `zQaLpyUFfNA` | Why Governments Fear Moral Truth |
| 83 | 345d | `wlRi_e-zzE4` | The Tribe of Ephraim — A Watchman in the House of God |
| 98 | 423d | `p0xBHbtk7CI` | Powerful Biblical Knowledge That Nobody Talks About |
| 100 | 397d | `2e_pe-3GpBI` | The SHOCKING Reality of How Nations Fall From Within |
| 104 | 427d | `Ox_dozHLaaM` | The Hidden Truth About Biblical Identity That Will SHOCK You! |
| 123 | 349d | `CuNKO1aBdRM` | The Tribe of Ephraim — Scattered but Never Forgotten |
| 133 | 343d | `6lbjD5o_ulk` | This 12 Tribes Prophecy Changes Everything |
| 145 | 416d | `puRpiE4KtXQ` | Deuteronomy 7:6-7 — "For thou art an holy people..." |
| 149 | 352d | `4-lwx45nL1A` | The Tribe of Ephraim — Arrows Against the Enemy |
| 163 | 418d | `V1X-iqGgYls` | Journey with us, The Most High Chosen People! |
| 170 | 360d | `U9Odey7BrxE` | The Tribe of Naphtali — Possess Thou the West and the South |
| 185 | 362d | `YZOq2NBT3d8` | The Tribe of Asher — Dipping His Foot in Oil |
| 192 | 359d | `w8fXqQPM26o` | The Tribe of Naphtali — Full of the Blessing of the Lord |
| 197 | 275d | `FEkLq5XApX0` | The Everlasting Covenant Israel's Promise |

## Tier B — Tribe-series tail (4 videos) — DELETE

**Criteria:** Part of a 6+ video cluster for the same tribe, bottom of the view distribution, 350+ days old. The top performers for each tribe stay up — this trims the tail that creates the "template" evidence pattern.

| Views | Age | Video ID | Title | Cluster context |
|---:|---:|---|---|---|
| 208 | 358d | `TK82X4dOE7w` | The Tribe of Naphtali — Satisfied With Favor | Naphtali cluster has 7 Shorts; top is 2,059v. Unlist bottom 3 (this + 2 in Tier A). |
| 211 | 355d | `Mo1wDJhH3d8` | The Tribe of Ephraim — Fruitful in a Strange Land | Ephraim cluster has 6 Shorts; top is 9,608v. Unlist bottom 4 (this + 3 in Tier A). |
| 436 | 385d | `EVXPdM8tGcQ` | The Tribe of Judah — Sold Into Slavery, Psalms 83 Conspiracy | Judah cluster has 8 Shorts; top is 33,316v. Unlist bottom 2 (this + next row). |
| 487 | 385d | `hJZ3g3ThGik` | The Tribe of Judah — The Lion's Whelp Shall Rise Again | Same Judah cluster — large gap between 3,447v and this. |

## Tier C — Generic hype titles, no scripture anchor (4 videos) — DELETE

**Criteria:** 400+ days old, 200–500 views, handle-spam titles with no scripture reference or original framing. These are the clearest "minimal narrative value" matches.

| Views | Age | Video ID | Title |
|---:|---:|---|---|
| 219 | 427d | `3ase0yJE_Xs` | The 12 Tribes of Israel The Most High Holy People @AIBIBLEGOSPELS |
| 222 | 457d | `ggAF28BvCqY` | The Most High Chosen People How special and Holy they are |
| 226 | 429d | `sN_UHGSkArg` | Why These 12 Tribes Changed The World FOREVER |
| 339 | 427d | `dwd69b2G-gU` | The Hidden Truth About Biblical Identity That Will SHOCK You! |

---

## What's explicitly being KEPT

- **All long-form (69 videos)** — this is what YouTube wants more of, not less.
- **All Shorts over 500 views** — proven surface-able content.
- **All Shorts under 90 days old** — too new to judge.
- **Tribe-series top performers** for every tribe (Judah 33K, Zebulun 22K, Reuben 16K, Gad 15K, Ephraim 9.6K, Gad 8.6K, Issachar 6.7K, Naphtali 2K, Asher 2K, Benjamin 1.3K, Manasseh 737v top).
- **The 115K "12 Tribes origins" Short** (top performer, 70% retention).
- **The 15 scheduled/paused "12 Tribes" draft Shorts** — stay paused, don't publish until post-reapply.

## Catalog impact

| Metric | Before | After cull |
|---|---:|---:|
| Total public videos | 238 | 215 |
| Public Shorts | 169 | 146 |
| Public long-form | 69 | 69 |
| Long-form share of catalog | 29% | 32% |

The ratio shift is small but meaningful: every percentage point away from "dominantly Shorts" helps the reviewer see a more narrative-driven channel.

## Execution plan

1. ✅ Approved 2026-04-24.
2. Run `scripts/delete-cull.py` — single pass, all 23 deletions, 0.5s pause between calls.
3. Log results to `docs/changelog.md` with the kill list + date.
4. Leave catalog alone for 60+ days before the 2026-07-08 reapply so the change settles.

## Why delete (not unlist)

The reapply reviewer is a Trust & Safety / monetization reviewer with internal tooling that likely sees full upload history — including unlisted. Hiding from the public feed doesn't hide content from that reviewer. The suspension notice framed it at the channel level ("a significant portion of your channel does not comply") — removing the content from the channel is the literal action that addresses that framing. YouTube's own reapply guidance also uses the word "remove," not "hide."

Deletion is permanent. None of the 23 are recoverable once the script runs.

## Not in scope (deliberately)

- No metadata edits on remaining videos.
- No title rewrites.
- No new uploads until long-form production starts (Phase 4B).
- No deletions outside this list — anything not listed here stays public.
