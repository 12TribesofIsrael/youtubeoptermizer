---
name: ""
metadata: 
  node_type: memory
  ended: 2026-05-18T18:00:00Z
  project: youtubeoptermizer (AI Bible Gospels channel optimization)
  branch: main
  originSessionId: 9a9379a4-a54f-4582-892e-f286cf99730c
---

# Last Session — 2026-05-17 / 2026-05-18

## What the user wanted

Build a verbatim-preserving cinematic Bible-video pipeline that bypasses Custom Script Mode's Claude scene-generator (which paraphrases scripture) so the AI Bible Gospels channel can produce long-form deep dives at scale ahead of the YPP reapply gate on **2026-07-08**. The Edom / Genesis 49 video was the production target.

## What we did

- **Shipped Custom Script 2.0** — full pipeline. Committed as `af1990c`.
  - `scripts/script-to-scenes.py` — converter (Format v2 .txt → scenes.json) with auto-inject canonical identity stack (Black Hebrew Israelite / Caucasian Edomite / per-tribe nationality markers), light/heavy identity routing for baby/woman/child scenes, hard-blocked unsafe visual patterns, auto-split on >900 narration words.
  - `scripts/render-via-pipeline.py` — thin wrapper around ai-bible-gospels' `generate.py`. Auto-loads LoRA from `training/lora-config.json`, defaults Daniel voice (`onwK4e9ZLuTAKqWW03F9`), `--kling-model` selector.
  - `scripts/render-patch.py` — surgical re-render that mixes N fresh FLUX+Kling clips with reused-from-prior-log clips + new narration. Cuts re-render cost ~50%.
  - `scripts/train-flux-lora.py` — FLUX LoRA trainer (fal-ai/flux-lora-fast-training).
  - `scripts/scrape-fal-history-v2.py` — fal.ai tRPC history scraper (308 records, 156 unique FLUX, 153 with verbatim FLUX prompts as captions).
  - `scripts/organize-lora-references.py` + `scripts/rewrite-lora-captions.py` — dataset prep.
  - `scripts/sniff-fal-api.py` — found the dashboard's tRPC endpoint via network capture.

- **Three flag additions to sibling `C:/Users/Claude/ai-bible-gospels/workflows/custom-script/generate.py`** (scoped edit, defaults preserve prior behavior):
  - `--voice-id` — channel Daniel voice override
  - `--kling-model` — full model map (v1.6 → o3-pro)
  - `--lora-url` / `--lora-trigger` / `--lora-scale` — routes FLUX to `fal-ai/flux-lora` endpoint
  - Retry logic on FLUX + Kling (3 attempts, exponential backoff, fail-fast on 4xx)

- **Trained the first channel LoRA** — trigger word `aibgospels`, 148 captioned photoreal images (israelite 90 / greek 16 / roman 11 / scene 31), 1500 steps, ~5 min, ~$10. URL saved to `training/lora-config.json` (gitignored).

- **Produced Edom / Genesis 49 long-form video**:
  - Source script: `drafts/edom-genesis49-longform-2026-05-16.txt` (20 min target, Bible-in-Black archetype)
  - Verbatim 1611 KJV from `docs/1611KjvW_apocrypha - Copy.pdf` (verified via pdftotext)
  - Multiple test renders at v1.6 + LoRA, total ~$50-70 fal.ai burn across the session (multiple failed renders before framework solidified)
  - Final Part 1 patched + Part 2 v1.6 rendered. Tommy will do the production cut via Custom Script Mode + Kling v3.0 himself.

- **12 Tribes → Nationality mapping** — extracted from `G:/My Drive/AI BIBLE GOSPELS/Book Folders/12 Tribes Movie/The Prophecy Revealed/The Prophecy Revealed.txt`. Saved to `docs/tribes-to-nationalities.md`. Converter auto-injects nationality markers (Judah=African American, Issachar=Mexican/Aztec, Naphtali=Polynesian/Chilean, etc.) when a tribe name appears in `[Visual:]` cues.

- **Saved 5 durable memory files** (see Step 4 below).

## Decisions worth remembering

- **The converter IS the framework.** Identity language for each archetype lives in ONE place (`MELANATED_SUFFIX` / `LIGHT_MELANATED_SUFFIX` / `EDOM_SUFFIX` in `scripts/script-to-scenes.py`) and ALWAYS injects, regardless of whether source already has identity language. Redundancy is intentional — reinforces FLUX signal.
- **Light vs heavy identity path** — proved necessary 2026-05-17 when the newborn-twins render lost Esau's "red hair" because the heavy stack's "natural afro-textured hair in locs, braids, full beard" overrode the scene-specific marker. Light path now used on `newborn / baby / infant / child / woman / mother / pregnant / womb / Rebekah / Sarah ...` triggers.
- **Block list is hard-fail, not silent-substitute.** Converter raises `ValueError` on any source containing `embracing / embrace / kissing / kiss / face-to-face / romantic / lovers`. Locked after 2026-05-17 Jacob+Joseph mountaintop render produced what visually read as two men kissing. Cardinal rule: TWO MALE FIGURES never in any close-quarters pose.
- **fal-ai/flux-pro/v1.1-with-loras does NOT exist.** First attempt 404'd. The correct LoRA-enabled FLUX endpoint is `fal-ai/flux-lora` (FLUX-dev base + LoRA, not flux-pro). LoRA bias dominates so quality drop is minimal.
- **JSON2Video has a monthly time quota.** Hit it on first o3-pro Part 1 attempt — wasted ~$30 in Kling clips because the assembly failed. User topped up. Pre-check before any o3-pro full render.
- **Scrape via tRPC, not DOM walk.** fal.ai dashboard at `/dashboard/recent-history` paginates via tRPC endpoint `/api/trpc/requests.search?batch=1&input=...` with `limit:24, cursor:N`. BigQuery flag (`enableBqTrpc:true`) doesn't add data; aggregate query exhausts in 13 pages.
- **NFT trading-card images and ChatGPT-painterly thumbnails are WRONG style for the cinematic LoRA.** Surveyed `G:/My Drive/AI BIBLE GOSPELS/12 Tribes NFT, Videos and Movie/*JPEG` (272 images) — stylized 3D cartoons, would corrupt the photoreal LoRA. Used the tribes folder only as visual reference (per-tribe color/garment markers), not training data.

## Open threads / next session starts here

1. **Tommy renders the Edom script via Custom Script Mode + Kling v3.0 himself.** Script at `drafts/edom-genesis49-longform-2026-05-16.txt` — paste into `localhost:8000/custom`. Block list catches any unsafe rewrites. If Tommy wants me to fire v3.0 via the wrapper, command is:
   ```
   python scripts/render-via-pipeline.py output/scenes/edom-genesis49-part1-scenes.json --kling-model v3.0
   ```
2. **Production cut at o3-pro** pending Tommy's v3.0 review. Cost would be ~$50-70 for the full 39-scene video. Skip if v3.0 looks publication-ready.
3. **Tribe-specific photoreal LoRA** — future option. Currently all tribes handled via converter auto-injection (prompt engineering). If tribe scenes start being a quality bottleneck, train a second `aibgospels-tribes` LoRA on photoreal renders generated via prompt-engineering.
4. **YPP watch-hour math** — current pace 1,940 hr/yr, need 4,000 hr/yr by 2026-07-08 reapply. Edom long-form once published should move this if retention matches the existing `mAJS97kNC5E` (6,328 watch-min / 28d from 370 views). Re-check via `python scripts/export-fresh-analytics.py` 7 days after Edom publishes.

## Uncommitted work

```
 M analytics/post-optimization/Chart data.csv
 M analytics/post-optimization/Table data.csv
 M analytics/post-optimization/Totals.csv
?? analytics/Content.csv  (TikTok dashboard CSV)
?? analytics/FollowerActivity.csv  (TikTok)
?? analytics/FollowerGender.csv  (TikTok)
?? analytics/FollowerHistory.csv  (TikTok)
?? analytics/FollowerTopTerritories.csv  (TikTok)
?? analytics/Overview.csv  (TikTok)
?? analytics/Viewers.csv  (TikTok)
?? docs/ReviewEditScenes.md  (scratch from earlier — first 39 scenes Claude AI generated before the v2 converter existed)
?? scripts/tt-comments-classify.py  (unrelated leftover)
?? src/cta-overlay/  (unrelated leftover, probably Remotion)
?? training/  (gitignored)
?? output/  (gitignored)
```

The CSV diffs are routine analytics refreshes from a prior session, not part of this commit's scope. Decide next session whether to commit them or leave for the TikTok work stream.
