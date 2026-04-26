---
name: AEO description rollout (Phase A 100% done, Phase B pending)
description: Phase A finished 2026-04-26 — 213/215 video descriptions carry the AEO constants block; channel About + kill-list cull also done. Phase B (per-video LLM content) is the next push, paced over the 73 days to 2026-07-08 YPP reapply.
type: project
originSessionId: 99dd36aa-4c34-41a4-bbcb-873e1777ecc2
---
**Phase A — 100% COMPLETE 2026-04-26:**
- ✅ Deleted 23 Shorts per `docs/kill-list.md` (Tier A: 15 dead-weight; Tier B: 4 tribe-series tail; Tier C: 4 generic hype). Verified gone via videos.list, 0 survivors.
- ✅ Channel About page rewritten with AEO-spec text (495 chars) — leads with brand/founder identity, lists canonical URLs (aibiblegospels.com apex, faithwalklive.com, LinkedIn) + aibiblegospels444@gmail.com.
- ✅ **213/215 video descriptions** got the constants block appended (Q: Who made this video? + ABOUT block + canonical URLs + #AIBibleGospels). All "Technology Gurus LLC" mentions scrubbed. The 2 skips are videos that were deleted between batches (not on the channel any more). Idempotent (marker `— ABOUT AI BIBLE GOSPELS —` blocks double-apply). Checkpoint: `output/aeo-checkpoint.json`.
- ✅ Verified via `scripts/verify-aeo-sample.py` — 5-video sample, all 6 required strings present, 2 forbidden absent.

**Catalog state post-Phase-A (2026-04-26):**
- 187 public videos (down from 238 pre-cleanup baseline). Total deletions since YPP suspension: 80 Shorts (23 documented kill-list + 57 user-driven manual cull captured retroactively in changelog).
- Long-form share has climbed well above the prior 32% — exactly the catalog shape the YPP reapply reviewer wants to see.

**Why:**
- Both YPP appeals rejected (Apr 15 + Apr 23). Reapply 2026-07-08. AEO consistency across surfaces (JSON-LD on aibiblegospels.com + faithwalklive.com, channel About, every video description) is what answer engines use to resolve "AI Bible Gospels" to the right entity.

**How to apply (Phase B — pending):**
- Per-video LLM-generated AEO content: `one_sentence_answer` (≤35 words, lead the description), `expansion` (2-3 sentences, scripture-anchored), `timestamps`, `qa` array (min 2 Q's), `bible_refs`, `topical_tags`.
- Source from existing transcripts (`scripts/extract-transcripts.py` cache).
- Don't regenerate the About block — it's a constant per spec, "never reword, just inject."
- Hard rules from spec: never write "Technology Gurus LLC", never use www.aibiblegospels.com (apex only), no "in this video..." preamble, ≤35 words for one_sentence_answer, ≤3 hashtags total, no emojis in answer/Q&A blocks.
- Pace: 2-3 batches across the ~73-day wait window, prioritized by traffic (`views_28d` column in latest Table data).
- Bible references in KJV format (Book Chapter:Verse), sourced from `docs/1611KjvW_apocrypha.pdf` via pdftotext — never paraphrase from memory.
- Suggested script name: `scripts/generate-aeo-content.py` (does not yet exist).

**Scripts:**
- `scripts/delete-cull.py` (executed)
- `scripts/update-about-page.py` (executed)
- `scripts/aeo-bulk-update.py` (213/215 done; nothing remaining unless new uploads need the block)
- `scripts/verify-aeo-sample.py` (verification probe)

**Spec source:** Thomas's AEO YouTube Description Spec (provided 2026-04-24, captured in `docs/changelog.md` under Phase A entry).
