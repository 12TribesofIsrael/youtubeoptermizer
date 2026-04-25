---
name: AEO description rollout (Phase A done, Phase B pending)
description: 2026-04-24 cleanup — 23 Shorts deleted, About page rewritten, 167/215 video descriptions got AEO constants block; 47 remain (quota); Phase B (per-video LLM content) ramps up over YPP wait window
type: project
originSessionId: 59f450a5-e39f-499c-a6d9-39f08c0257e5
---
**Phase A — done 2026-04-24:**
- Deleted 23 Shorts per `docs/kill-list.md` (Tier A: 15 dead-weight; Tier B: 4 tribe-series tail; Tier C: 4 generic hype). Catalog 238 → 215.
- Channel About page rewritten with AEO-spec text (495 chars) — leads with brand/founder identity, lists canonical URLs (aibiblegospels.com apex, faithwalklive.com, LinkedIn) + aibiblegospels444@gmail.com.
- 167 of 215 video descriptions got the constants block appended (Q: Who made this video? + ABOUT block + canonical URLs + #AIBibleGospels). All "Technology Gurus LLC" mentions scrubbed. Idempotent (marker `— ABOUT AI BIBLE GOSPELS —` blocks double-apply).
- 47 videos remain — quota exhausted at video 169. Checkpoint: `output/aeo-checkpoint.json`. Resume: re-run `scripts/aeo-bulk-update.py` after PT midnight.

**Why:**
- Both YPP appeals rejected (Apr 15 + Apr 23). Reapply 2026-07-08. Cleanup IS allowed during the wait — old "no delete / no bulk-edit" rules were written for active-review state, retired post-denial.
- AEO consistency across surfaces (JSON-LD on aibiblegospels.com + faithwalklive.com, channel About, every video description) is what answer engines use to resolve "AI Bible Gospels" to the right entity. The constants block on every video is the highest-leverage piece — teaches AI Overviews / ChatGPT / Perplexity / Gemini / Copilot to cite the channel by name.

**How to apply (Phase B — pending):**
- Per-video LLM-generated AEO content: `one_sentence_answer` (≤35 words, lead the description), `expansion` (2-3 sentences, scripture-anchored), `timestamps`, `qa` array (min 2 Q's), `bible_refs`, `topical_tags`.
- Source from existing transcripts (`scripts/extract-transcripts.py` cache).
- Don't regenerate the About block — it's a constant per spec, "never reword, just inject."
- Hard rules from spec: never write "Technology Gurus LLC", never use www.aibiblegospels.com (apex only), no "in this video..." preamble, ≤35 words for one_sentence_answer, ≤3 hashtags total, no emojis in answer/Q&A blocks.
- Pace: 2-3 batches across the 75-day wait window, prioritized by traffic.
- Bible references in KJV format (Book Chapter:Verse), sourced from `docs/1611KjvW_apocrypha.pdf` via pdftotext — never paraphrase from memory.

**Scripts:**
- `scripts/delete-cull.py` (executed)
- `scripts/update-about-page.py` (executed)
- `scripts/aeo-bulk-update.py` (167/215 done, resume tomorrow)
- `scripts/verify-aeo-sample.py` (verification probe)

**Spec source:** Thomas's AEO YouTube Description Spec (provided 2026-04-24, captured in `docs/changelog.md` under Phase A entry).
