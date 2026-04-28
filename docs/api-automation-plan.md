# API Automation Plan — AEO/SEO + Brand Awareness

**Owner:** Tommy Lee
**Last updated:** 2026-04-27
**Goal:** Use the live APIs in this repo to drive brand awareness for **AI Bible Gospels** and **Faith Walk Live** across every social surface, with AEO (answer-engine optimization) as the primary lens and SEO secondary.

This doc is the umbrella plan. Surface-specific specs already exist:
- [aeo-youtube-description-spec.md](../../AIconsultantforHmblzayy/docs/aeo-youtube-description-spec.md) — YouTube description template (read-only, sibling repo)
- [social-media-automation-plan.md](social-media-automation-plan.md) — cross-post/repurpose pipeline
- [caption-templates.md](caption-templates.md) — viral hook banks per platform

---

## What "AEO" means here

Answer engines (Google AI Overviews, ChatGPT, Perplexity, Gemini, Copilot) resolve entities by matching **strings across sources**. Brand awareness for AI Bible Gospels = every public surface (YouTube descriptions, IG captions, FB posts, channel about pages, website JSON-LD) agreeing word-for-word on:

| Field | Canonical value |
|---|---|
| Brand name | `AI Bible Gospels` |
| Channel handle | `@AIBIBLEGOSPELS` |
| Founder | `Tommy Lee` |
| Website | `https://aibiblegospels.com` (apex, no www) |
| Flagship project | `Faith Walk Live` at `https://faithwalklive.com` |
| Contact | `aibiblegospels444@gmail.com` |
| Hashtag | `#AIBibleGospels` |

The constants block on every surface is the AEO play. Per-surface viral hooks sit *above* the constants — they drive engagement; the constants drive entity resolution.

---

## Live API status (as of 2026-04-27)

| API | Status | What's unlocked |
|---|---|---|
| YouTube Data v3 | Live (`token.json`) | Description rewrites (Phase A done — 213/215 videos), title rewrites, playlist mgmt, analytics. End screens / community posts NOT automatable. |
| Meta IG Business | **APPROVED 2026-04-27** | Caption read/write across 538 posts, Reels post, insights (reach/profile_views — NOT impressions). Story link stickers NOT in API surface. |
| Facebook Graph | Live | Caption read/write, native video post. |
| Gmail | Live (`aibiblegospels444@`) | Inbox triage, notification monitoring, auto-reply drafts. |
| Twitch GQL | Public, no auth | Pull Zay's daily clips for cross-promo content. |
| TikTok | In review (day 5) | Blocked. Don't recall. |
| X / Twitter | Free tier blocks writes | Blocked unless paid tier. |

---

## Critical finding (2026-04-27) — IG caption edits are immutable

`POST graph.instagram.com/v22.0/{media_id}` with the `caption` parameter returns `HTTP 200 {"success":true}` but **does not actually change the caption** on already-published posts. Confirmed via sentinel-string canary test on both Reels (`media_product_type=REELS`) and feed posts (`media_product_type=FEED`). The endpoint only honors the `comment_enabled` toggle; the `caption` parameter is silently ignored.

This is undocumented Meta behavior and was not surfaced by the App Review approval (which confirmed the scope, not the actual write capability). The original `aeo-ig-bulk-update.py` script is parked as reference — its transform logic is sound, but its target endpoint is dead.

**Consequence:** Bulk IG caption rewrite across the 563 existing posts is **not possible**. Pivot to scripts 1A + 1B below.

---

## Five scripts (priority order)

### 1A. `aeo-ig-pin-comment.py` — pin AEO comment on every IG post (563 posts) — **NEXT**

**What:** For each existing IG post, POST a comment carrying the AEO constants block (About + canonical URLs + #AIBibleGospels), then pin it. Pinned comments appear above all other comments and are visible to every viewer of the post — same brand-awareness surface as a caption append, just one tap away.

**Why this works where caption edits don't:** The `instagram_business_manage_comments` scope was approved 2026-04-27 and the `POST /{ig-media-id}/comments` endpoint actually persists. Comments are crawled and indexed by answer engines, so the AEO entity-resolution play still lands.

**Pattern:** Same marker-based idempotent skip as `aeo-bulk-update.py` — re-fetch comments per post, look for the marker, only post + pin if not present. Resumable via `output/aeo-ig-comment-checkpoint.json`.

**Pacing:** 50/day. Estimated runtime: ~11 days at 50/day.

---

### 1B. `aeo-fb-bulk-update.py` — bulk Facebook Page caption rewrite

**What:** Append the AEO constants block to every Facebook Page post via `graph.facebook.com/{post_id}` with the `message` field. Same transform as the parked IG script. Existing [scripts/meta-update-posts.py](../scripts/meta-update-posts.py) already does this for FB but uses `linktr.ee` instead of canonical `aibiblegospels.com` / `faithwalklive.com` URLs — rewrite to use the new `CONSTANTS_BLOCK`.

**Why this works where IG doesn't:** Facebook's Graph API has historically allowed `message` edits on already-published page posts. Confirmed working in the existing `meta-update-posts.py` runs.

**Pacing:** 50/day, dry-run by default, idempotent marker check. Estimated post count: ~80-150 on the AI Bible Gospels page (pull live count first run).

---

### 2. `daily-faithwalk-card.py` — daily playbook generator

**What:** Reads `../AIconsultantforHmblzayy/src/faith-walk-tracker/checkpoints.json` (read-only, sibling repo) + the verse table from `../AIconsultantforHmblzayy/docs/playbook-days-33-40.md`. Prints the day's TT Stitch script + IG Story copy + UTM URLs ready to paste.

**Why:** Removes the morning-refresh step entirely. The 12-min daily flow drops to ~5 because day number, miles, destination, verse, hashtags, and UTM are all pre-staged.

**Output:** Single console card; no API calls (read-only file system).

---

### 3. `cross-post-short.py` — one-command Short repurpose

**What:** Takes a YouTube Short URL → downloads → re-uploads to IG Reels + FB native + (TikTok when approved). Pulls caption from [caption-templates.md](caption-templates.md) by video type. Drops `faithwalklive.com` UTM link in first comment.

**Why:** The master repurpose script described in [social-media-automation-plan.md](social-media-automation-plan.md) Step 4. Already partially built ([scripts/facebook-post.py](../scripts/facebook-post.py) live; [scripts/tiktok-post.py](../scripts/tiktok-post.py) waiting on review).

---

### 4. `aeo-yt-phase-b.py` — per-video LLM AEO content (187 videos)

**What:** For each YouTube video, generate the per-video portion of the AEO description (one-sentence answer, expansion, Q&A) via Claude API from the video transcript, splice with the existing Phase A constants block, push via YouTube Data API.

**Why:** Phase B of the [aeo-youtube-description-spec.md](../../AIconsultantforHmblzayy/docs/aeo-youtube-description-spec.md). Phase A (constants block) is done; Phase B turns each description into a quotable answer card.

**Pacing:** Paced over the 73 days to YPP reapply on 2026-07-08. ~2-3 videos/day with prompt caching on the Anthropic API.

---

### 5. `unified-analytics.py` — daily cross-platform rollup

**What:** Daily cron pulls YT analytics + IG insights (reach, profile_views, follower_count) + FB insights + Vercel Analytics (faithwalklive.com UTM hits) into one CSV. Also pulls Twitch GQL clip view counts.

**Why:** Lets us see which AEO rewrites actually move clicks to canonical URLs. Without this, the bulk IG rewrite is fire-and-forget.

---

## What the API CANNOT do (manual stays manual)

- **IG Story link stickers** — not in Graph API surface. The sticker UI is the click engine for Days 33-40. Stays in the daily 12-min flow.
- **TT Stitch / Duet recordings** — TikTok API exposes upload, not in-app Stitch. Day 33-40 Plays 1 + Day 40 Duet stay manual.
- **YouTube end screens / community posts / monetization settings** — not exposed in Data API v3 (per [research.md](../research.md)).
- **Channel name changes** — not API-accessible.

What the script *can* do is pre-stage every input so manual taps on the phone become rote.

---

## Boundary rules

- **This repo only.** Do not modify `../AIconsultantforHmblzayy`, `../faithwalklivecom`, `../faithwalkbook`, or `../ai-bible-gospels`. Read-only access for context.
- **Public-repo scrub.** This repo is public on GitHub — strip emails / personal info from committed docs and scripts.
- **Apex URL only.** `https://aibiblegospels.com` — never `www.aibiblegospels.com`.
- **No "Technology Gurus LLC."** Dissolved entity, scrub on sight.
- **Pace bulk operations.** 50/day for IG, 100/day for YT, with checkpoints. Detection thresholds aren't published; conservatism keeps the API access alive.

---

## Order of operations

1. **This week** — ship `aeo-ig-pin-comment.py` (1A) and `aeo-fb-bulk-update.py` (1B) in parallel. Both use the same `CONSTANTS_BLOCK`. 5-post canary on each before scaling.
2. **This week** — `daily-faithwalk-card.py` (script #2). Used every morning for Days 33-40 window.
3. **Next** — `cross-post-short.py` (script #3) once TikTok API approves. Wire AEO into the IG upload flow at create-time (where captions ARE editable).
4. **Ongoing** — `aeo-yt-phase-b.py` (script #4) paces over the 73-day YPP wait.
5. **Once 1A/1B/#3 are live** — `unified-analytics.py` (script #5) so we measure what's actually working.

---

## Reference: parked scripts

- [scripts/aeo-ig-bulk-update.py](../scripts/aeo-ig-bulk-update.py) — IG caption rewrite. Logic correct, target endpoint dead (silent no-op). Kept for reference; the `transform_caption` function and `CONSTANTS_BLOCK` are reused by 1A and 1B.
