# System Inventory — youtubeoptermizer

**Last Updated:** April 17, 2026
**Channel:** AI Bible Gospels (@AIBIBLEGOSPELS)
**Repo:** github.com/12TribesofIsrael/youtubeoptermizer

---

## Quick Stats

- **24 automation scripts** across YouTube, Facebook, Instagram, X/Twitter
- **8-route FastAPI web dashboard** with analytics, video management, social posting, and tools
- **14 strategy/reference docs**
- **5 platform integrations** (YouTube, Facebook, Instagram, X, OpenAI)
- **583 Instagram posts**, **245 YouTube videos**, **14 playlists**

---

## Platform Status (April 17, 2026)

| Platform | Connected | Can Post | Can Edit | Status |
|----------|-----------|----------|----------|--------|
| YouTube | Yes | Yes | Yes | Active — full API access |
| Facebook | Yes | Yes | Yes | Live — 8 posts published April 1 |
| Instagram | Yes | Read only | No | App Review submitted 4/17 — waiting approval |
| X/Twitter | Keys saved | No | No | Free tier blocks API posting |
| TikTok | No | No | No | Using Repurpose.io instead |

---

## Scripts (24 total)

### YouTube — Channel Management

| Script | What it does |
|--------|-------------|
| `scripts/connect.py` | One-time OAuth setup — opens browser for Google authorization |
| `scripts/test-connection.py` | Verify YouTube API credentials work |
| `scripts/channel-status.py` | Pull live metrics: subscribers, views, video count |
| `scripts/check-quota.py` | Estimate daily API quota usage |
| `scripts/full-audit.py` | Scan all videos, flag issues: duplicates, short, low performers |
| `scripts/export-current-data.py` | Export all videos to CSV for baseline tracking |
| `scripts/export-fresh-analytics.py` | Export fresh analytics snapshot for before/after comparison |
| `scripts/extract-transcripts.py` | Pull transcripts from "Part" videos to identify tribe topics |
| `scripts/extract-remaining.py` | Retry transcript extraction for videos that failed |
| `scripts/generate-titles.py` | Analyze transcripts, suggest standalone searchable titles |
| `scripts/thumbnail-priorities.py` | Rank videos by impressions/CTR for thumbnail priority |

### YouTube — Bulk Edits & Cleanup

| Script | What it does |
|--------|-------------|
| `scripts/fix-handle-titles.py` | Remove @AIBIBLEGOSPELS from all video titles (154 fixed) |
| `scripts/fix-dashes.py` | Fix broken em dash UTF-8 encoding (50 fixed) |
| `scripts/rename-parts.py` | Rename "Part X" to standalone titles, move part # to description (58 done) |
| `scripts/rename-remaining.py` | Process remaining Part videos with fallback naming (26 done) |
| `scripts/delete-duplicates.py` | Delete lower-view duplicates of same part numbers (10 deleted) |
| `scripts/delete-matthew6.py` | Delete 5 near-identical "Matthew 6" flood videos |
| `scripts/delete-short-and-low.py` | Delete videos under 15 seconds or under 30 views (13 deleted) |
| `scripts/upload-thumbnails.py` | Batch upload custom thumbnails from /thumbnails folder (20 uploaded) |
| `scripts/create-playlists.py` | Create 14 tribe-based playlists with video assignments |
| `scripts/reorganize-playlists.py` | Reorganize playlists by tribe/topic |

### Meta — Facebook & Instagram

| Script | What it does |
|--------|-------------|
| `scripts/facebook-post.py` | Post 8 viral posts to Facebook Page with YouTube CTAs |
| `scripts/meta-update-posts.py` | Update captions on all 538 IG + FB posts with viral hooks and hashtags |
| `scripts/fix-facebook-captions.py` | Strip AI garbage appended by Repurpose.io from FB posts |
| `scripts/meta-ig-business-review.py` | Instagram Business Login OAuth + App Review test calls (the correct script) |
| `scripts/meta-app-review.py` | OLD — Playwright browser OAuth for FB-based test calls (do not use for instagram_business_*) |
| `scripts/meta-test-calls.py` | OLD — test calls via graph.facebook.com (do not use for instagram_business_*) |
| `scripts/meta-open-testing.py` | Opens Meta Testing dashboard in Playwright browser |

### X/Twitter

| Script | What it does |
|--------|-------------|
| `scripts/twitter-post.py` | 8 viral tweet templates ready (blocked — Free tier can't post) |

### TikTok

| Script | What it does |
|--------|-------------|
| `scripts/tiktok-post.py` | OAuth flow (TikTok Login Kit) + video upload via Content Posting API. Supports inbox (drafts) and direct publish modes. Chunked upload, automatic token refresh, sandbox-friendly. |

### Content Generation

| Script | What it does |
|--------|-------------|
| `scripts/generate-scripture-cards.py` | Generate Deuteronomy 28 scripture card images via OpenAI DALL-E (1792x1024 PNG) |

---

## Web Dashboard (FastAPI)

**Entry point:** `app.py`
**Run:** `uvicorn app:app --reload`

| Page | Route | Features |
|------|-------|----------|
| Dashboard | `/` | Live channel stats, recent uploads, quick action buttons |
| Analytics | `/analytics` | Time-series views/watch-time/subscribers, top video rankings |
| Videos | `/videos` | List, search, bulk update titles/descriptions, delete |
| Playlists | `/playlists` | Create, organize, add/remove videos |
| Social | `/social` | Post to Facebook/Instagram/X, dry-run preview, live mode |
| Audit | `/audit` | Full channel audit with issue categories and impact scores |
| Tools | `/tools` | Thumbnail generator (DALL-E), transcript extractor, title suggester |
| Settings | `/settings` | API key configuration, platform connection status |

### API Endpoints (37 total)

All routes defined in `src/routes/` — dashboard.py, analytics.py, videos.py, playlists.py, audit.py, social.py, tools.py, settings.py.

---

## Core Library (`src/`)

### src/youtube/

| File | Purpose |
|------|---------|
| `auth.py` | OAuth 2.0 — loads credentials, manages token refresh (scopes: youtube.force-ssl, youtube.upload, yt-analytics.readonly) |
| `client.py` | YouTubeClient class — list_videos, get_video, update_video, delete_video, set_thumbnail, create_playlist, add_to_playlist |

### src/social/

| File | Purpose |
|------|---------|
| `facebook.py` | 8 pre-configured viral post templates for Facebook Page |
| `twitter.py` | 8 pre-configured viral tweet templates with hashtags |
| `meta_updater.py` | Hook banks (identity, prophecy, truth, awe) for caption updates + deterministic hook picker |
| `caption_cleaner.py` | Strip Repurpose.io AI garbage from captions |

### src/routes/

8 FastAPI route files powering the web dashboard (see table above).

### src/audit-app/

Standalone audit SaaS — FastAPI app that uses Claude API to generate comprehensive YouTube/social media audit reports as PDF.

---

## Analytics Data

| File | Contents |
|------|----------|
| `analytics/audit-results.json` | Full initial audit — all videos categorized by issue type |
| `analytics/part-topics.json` | Transcript analysis for 80+ Part videos — tribe/topic identification |
| `analytics/proposed-titles.json` | Generated standalone titles for 58 Part videos |
| `analytics/transcript-errors.json` | 26 failed transcript extractions (IP block) |
| `analytics/Table data.csv` | Per-video analytics: views, retention, CTR, watch time, impressions |
| `analytics/Chart data.csv` | Year-over-year average view duration trends |
| `analytics/Totals.csv` | Annual average view duration totals |
| `analytics/pre-optimization/` | Baseline data snapshots before changes |
| `analytics/post-optimization/` | Post-optimization comparison data |

---

## Documentation (14 files)

### Strategy & Planning

| Doc | What it covers |
|-----|---------------|
| `docs/project-plan.md` | Full 5-phase roadmap with timelines and priorities |
| `docs/status.md` | Master status — platform APIs, what's done, what's next |
| `docs/changelog.md` | Every change made with dates, reasons, and measurement plans |
| `docs/competitors.md` | Competitor analysis: BibleProject (5.3M), AI Bible Stories (1.1M), AI Bible Sagas (110K), The Bible in Black (47.5K) |
| `docs/social-media-audit.md` | 4-platform audit with benchmarks and growth strategies |
| `docs/social-media-automation-plan.md` | Automation strategy and tool selection per platform |

### Content & Templates

| Doc | What it covers |
|-----|---------------|
| `docs/caption-templates.md` | Master caption system by video type (Tribe Reveal, Scripture Drop, Prophecy, Awe) |
| `docs/repurpose-templates.md` | Pre-formatted captions for Repurpose.io workflows (IG, TikTok, FB, X) |
| `docs/kling-prompt-rules.txt` | Kling AI video prompt rules — no text in prompts, melanated characters mandatory |
| `docs/bible-movie-series-plan.md` | 81-book, 18-season biblical movie series plan using AI video generation |
| `docs/seamlessbiblicaltimeline.md` | Biblical timeline content strategy |
| `docs/movie-director-usage.md` | Movie Director skill documentation for video pipeline |

### Technical Reference

| Doc | What it covers |
|-----|---------------|
| `docs/meta-instagram-api-guide.md` | Complete Meta Instagram Business API guide — setup, App Review, bugs, client onboarding runbook |
| `docs/AI Bible GospelsSystemOverview.md` | System architecture overview |

### Reference PDFs

| Doc | What it covers |
|-----|---------------|
| `docs/1611KjvW_apocrypha - Copy.pdf` | KJV 1611 Apocrypha — reference material |
| `docs/Genealogy_of_Jesus_pictures2-locked.pdf` | Genealogy of Jesus visual reference |

---

## Web UI Templates (10 HTML files)

`templates/` — base.html, dashboard.html, analytics.html, videos.html, playlists.html, social.html, audit.html, tools.html, settings.html, about.html

## Static Assets

`static/js/app.js` — Frontend JavaScript for API calls, forms, charts
`static/css/` — Brand-styled CSS
`static/img/` — Logo and UI assets

---

## Environment Variables (.env)

| Variable | Service | Notes |
|----------|---------|-------|
| `ANTHROPIC_API_KEY` | Claude API | For audit report generation |
| `OPENAI_API_KEY` | OpenAI/DALL-E | Scripture card and thumbnail generation |
| `META_ACCESS_TOKEN` | Facebook Graph API | Expires ~60 days |
| `META_APP_ID` | Facebook App | 1452257036358754 |
| `META_APP_SECRET` | Facebook App | — |
| `FACEBOOK_PAGE_ID` | Facebook Page | 601690023018873 |
| `INSTAGRAM_BUSINESS_ID` | IG Business Account (FB API) | 17841454335324028 |
| `IG_APP_ID` | Instagram App (IG API) | 922450807234394 |
| `IG_APP_SECRET` | Instagram App | — |
| `IG_BUSINESS_TOKEN` | Instagram Business Login | Expires ~60 days |
| `TWITTER_API_KEY` | X/Twitter | Free tier — can't post |
| `TWITTER_API_SECRET` | X/Twitter | — |
| `TWITTER_ACCESS_TOKEN` | X/Twitter | — |
| `TWITTER_ACCESS_SECRET` | X/Twitter | — |

YouTube OAuth uses `credentials.json` + `token.json` (not .env).

---

## Optimization Progress

| Phase | Status | Key Results |
|-------|--------|-------------|
| 1. Channel Cleanup | Done | 30 videos deleted, 154 titles cleaned |
| 2. Title Optimization | Done | 84 Part titles renamed to standalone, 50 em dash fixes |
| 3. Thumbnails | Done | 20 custom thumbnails, brand guide locked |
| 4A. Playlists + Trailer | Done | 14/14 playlists, trailer script ready |
| 4B. Long-form Content | In Progress | First pillar video script written |
| 5. Social Media | In Progress | FB live, IG pending App Review, X blocked by free tier |

---

## Repurpose.io (External — Not in Codebase)

Handles automated cross-posting from Google Drive to 4 platforms at 9am/6pm daily. Cannot edit existing posts or generate content. Caption templates are manually configured in the Repurpose dashboard — source templates stored in `docs/repurpose-templates.md`.

---

## Brand Identity (Locked March 17, 2026)

- **Colors:** Deep navy #0A0A2A, divine gold #E8C46B, warm amber #D4A04A, bronze #8B5E3C
- **Lighting:** Dramatic chiaroscuro — golden light through darkness
- **Font:** Bold gold serif with subtle glow
- **Characters:** Melanated Black/African American depictions (mandatory in ALL AI prompts)
- **Mood:** Cinematic, revelatory, powerful
- **Full palette:** See `brand-colors.md`
