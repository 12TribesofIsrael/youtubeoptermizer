---
name: ""
metadata: 
  node_type: memory
  ended: 2026-07-17T22:30:00-04:00
  project: youtubeoptermizer (AI Bible Gospels)
  branch: main
  originSessionId: e880ab15-018e-4a34-98c6-9e572112c856
---

# Last Session — 2026-07-17

## What the user wanted
Ship the finished Eden→Timbuktu documentary: run post-production (intro/outro/logo),
upload it to YouTube with a full viral metadata pack + a controversial-but-professional
pinned comment, and make a viral thumbnail. Then commit + push.

## What we did
- **Post-production**: ran `scripts/post_produce.py output/renders/eden-full-doc.mp4 --width 1920`.
  Output `output/eden-full-doc_final.mp4` — 97.3 min / 1920x1080 / ~1.82 GB (main 94.7min +
  27.6s intro + ~128s outro). Gitignored (`*.mp4`), stays local.
- **Uploaded to YouTube as UNLISTED** via new `scripts/upload-eden-full-doc.py`.
  **video_id = `jnfMCN4cuv4`** (https://www.youtube.com/watch?v=jnfMCN4cuv4).
  - Viral description (hook + 13 real chapters computed from scene mp4 durations, intro-offset
    aware +27.6s; Windsor credited; Telegram link; Q&A; AI-transparency block).
  - 18 keyword tags (had to TRIM from 30 — see memory [[feedback_yt_tag_500_char_cap]]).
  - Thumbnail set to `output/thumbnails/eden-full/02_erased.png`.
  - Playlist "From Eden to Timbuktu" created (id `PLJBvvTjw_xRQ`) + video added.
  - Pinned-comment text posted (comment_id Ugz9D9r6APKfn9hidfp4AaABAg) — Pin click is Studio-only.
- **Viral thumbnails**: new `scripts/generate-eden-full-thumbnail.py` — 3 variants at 1280x720 in
  `output/thumbnails/eden-full/` (01_hebrews, 02_erased, 03_origin). fal FLUX-pro bg + PIL
  gold-serif typeset text. See [[reference_viral_thumbnail_generator]].
- **Committed + pushed** `7dae493` (both new scripts only; thumbnails/mp4 gitignored).

## Decisions worth remembering
- **Unlisted-first, not straight-to-Public.** Mirrors Part 1 + anchor-doc pattern. Rationale:
  the Altered/synthetic-content flag + the Pin click are Studio-only manual steps, and Public is
  the irreversible move. Tommy flips it after QC.
- **Thumbnail text via PIL, not the model.** FLUX/gpt-image garble letters; model renders the
  LIGHT, PIL renders the WORDS (Constantia Bold gold + dark stroke + glow). Correct by construction.
- **Recommended lead thumbnail = 02_erased** ("THE HISTORY THEY ERASED", close-up direct gaze) —
  highest expected CTR. Alternatives 01_hebrews (identity flag), 03_origin (epic wide).

## Open threads / next session starts here
1. **Go-live punch list for Tommy (video jnfMCN4cuv4, currently UNLISTED):**
   (a) QC the encoded player, (b) Studio > Show more > Altered/synthetic content = YES,
   (c) Comments > Pin the posted comment, (d) confirm/swap thumbnail, (e) Visibility = Public/Schedule.
2. Thumbnail swap is one line in `upload-eden-full-doc.py` (THUMBNAIL=) OR just done in Studio.
3. fal balance nudged ~15¢ (3 FLUX-pro thumbnail calls) — still inside the -$20 buffer.

## Uncommitted work
Clean working tree. `7dae493` pushed to origin.
