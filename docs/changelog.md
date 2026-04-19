# Channel Optimization Changelog

Track every change made to the AI BIBLE GOSPELS channel, with dates and expected impact on analytics.

---

## Baseline Metrics (Before Optimization)
**Snapshot Date:** March 16, 2026

| Metric | Value |
|--------|-------|
| Subscribers | 5,876 |
| Total Views | 764,290 |
| Total Videos | 268 |
| Avg View % | 66% (Shorts), 50.92% (all) |
| Impressions CTR | 4.06% |
| Top Video | 12 Tribes Origins — 115K views |

---

## Changes Log

### March 16, 2026 — Initial Cleanup

#### 1. Removed @AIBIBLEGOSPELS from 154 titles
- **Time:** ~3 minutes (API batch)
- **Videos affected:** 154
- **Why:** Handle in title truncates the actual title in YouTube search results, hurting CTR
- **Expected impact:** +0.5-1% CTR improvement from titles being fully visible
- **How to measure:** Compare impressions CTR in YouTube Studio for the 2-week period after vs before. Filter to videos that were changed.

#### 2. Deleted 10 duplicate part-numbered videos
- **Time:** ~1 minute (API batch)
- **Videos deleted:**
  - Part 11 duplicate (9,728 views) — kept 59,920-view version
  - Part 10 duplicate (2,250 views) — kept 19,415-view version
  - Part 8 duplicate (1,178 views) — kept 16,962-view version
  - Part 15 duplicate (5,095 views) — kept 8,274-view version
  - Part 22 duplicate (3,651 views) — kept 7,853-view version
  - Part 23 duplicate (986 views) — kept 2,435-view version
  - Part 66 duplicate (1,545 views) — kept 9,608-view version
  - Part 75 duplicate (727 views) — kept 737-view version
  - Part 52 duplicates x2 (145 + 118 views) — kept 1,593-view version
- **Why:** Duplicate part numbers confuse playlist SEO and returning viewers, signal spam to algorithm
- **Expected impact:** Cleaner playlist navigation, reduced algorithm spam signals

#### 3. Deleted 5 Matthew 6 flood videos
- **Time:** ~30 seconds (API batch)
- **Videos deleted:** 5 near-identical "Matthew 6" / "Book of Matthew 6" videos posted same day
- **Kept:** "Book of Matthew 6 #godsays #motivation..." (740 views)
- **Why:** 7 near-identical videos uploaded on March 8 diluted channel authority, looked like spam
- **Expected impact:** Reduced spam signals to algorithm, improved channel authority score

#### 4. Deleted 13 very short (<15s) and low-performing (<30 views) videos
- **Time:** ~1 minute (API batch, hit quota on last 2)
- **Videos deleted:** 13 (4 short + 9 low performers)
- **Remaining (deleted manually):** KVWUcoV2nOI (25 views), mvQ4BQILSd8 (26 views)
- **Why:** Sub-15s videos can't monetize as Shorts. Low performers drag channel average and signal weak content.
- **Expected impact:** Higher channel-wide averages for CTR and retention

#### Summary — March 16, 2026
| Action | Count |
|--------|-------|
| Titles cleaned | 154 |
| Videos deleted | 30 |
| **Total videos after cleanup** | **~238** |

---

### March 17, 2026 — Part Title Renames (Phase 2)

#### 5. Renamed 58 "Part X" videos to standalone searchable titles
- **Videos affected:** 58
- **Method:** Extracted transcripts via YouTube Transcript API, identified the specific tribe/topic each video covers, crafted unique standalone titles
- **Part numbers moved to descriptions** ("Part X of The Prophecy Revealed series")
- **Why:** "Part 44" means nothing to new viewers. "Aztecs and the Day of the Dead — Ancient Babylonian Connection" ranks in search forever.
- **Expected impact:** Major increase in search traffic, impressions, and CTR from non-subscribers
- **How to measure:** Compare search impressions and CTR for renamed videos over 2-4 weeks
- **Remaining:** 26 Part videos had no transcripts available — will handle in a future batch

#### Summary — March 17, 2026
| Action | Count |
|--------|-------|
| Part titles renamed to standalone | 58 |
| Part numbers moved to descriptions | 58 |

---

### March 17, 2026 — Phase 3: Thumbnail Optimization (Batch 1)

#### 6. New channel banner and profile picture
- **Why:** Old branding was generic. New assets match cinematic gold/navy brand identity inspired by competitor analysis of The Bible in Black (47.5K subs)
- **Brand guide locked:** Dark navy/black backgrounds, golden/amber light, bold gold serif font, dark-skinned biblical figures, dramatic chiaroscuro lighting

#### 7. Uploaded 10 custom thumbnails for highest-impression videos
- **Videos affected:** 10 (prioritized by highest impressions with lowest CTR)
- **Method:** Generated via ChatGPT/DALL-E using brand guide, then batch uploaded via API
- **Technical note:** DALL-E outputs were 3-5MB PNGs. YouTube thumbnail limit is 2MB. Compressed to JPEG (quality 85, resized to 1280x720) using Pillow — final sizes 165-259 KB each.
- **Thumbnail formula:** Bold 3-5 word gold text overlay + close-up biblical figure + dark background with golden light
- **Videos updated:**

| Video ID | Title | Impressions | CTR Before | Text on Thumbnail |
|----------|-------|-------------|------------|-------------------|
| mAJS97kNC5E | The Prophecy Revealed — Official Movie | 116,186 | 4.37% | PROPHECY REVEALED |
| UObM30FGdSs | The 12 Tribes Origins | 99,947 | 4.52% | 12 TRIBES ORIGIN |
| Zs2ctQoZmhU | Full Breakdown of the 12 Tribes | 37,836 | 4.46% | TRIBES DECODED |
| DEYNUT9uoxM | 12 Tribes — Tribe of Judah | 21,101 | 3.19% | TRIBE OF JUDAH |
| H9jblXXVHxY | Where Did the Lost Tribes Go? | 13,184 | 3.31% | WHERE DID THEY GO? |
| xL8v7eZ9mwc | The Prophecy Revealed AUDIO BOOK | 12,238 | 1.85% | AUDIO BIBLE |
| dpERIR0YZZ8 | Most Powerful Biblical Discovery SECRET | 11,802 | 3.30% | THEY HID THIS |
| Ad3mUsbLL3w | The Chosen — Teaser Trailer | 10,430 | 3.89% | THE CHOSEN |
| PCxBqyvr8NA | Lost Tribes Blessings — Deut 28 | 8,985 | 2.74% | BLESSINGS REVEALED |
| rq27Uvxudwg | Who and Where Are the Lost 12 Tribes | 7,907 | 3.29% | FOUND THEM |

- **Expected impact:** +1-2% CTR on these videos. At 380K combined impressions, even +1% CTR = ~3,800 additional clicks
- **How to measure:** Compare CTR for these 10 videos in YouTube Studio over 2-4 weeks
- **Quota cost:** 500 units (50 per thumbnail × 10)

#### 8. Uploaded 10 more custom thumbnails (Batch 2)
- **Videos affected:** 10 long-form videos (next highest impressions)
- **Method:** Same as Batch 1 — DALL-E generation, Pillow compression (PNG→JPEG, 167-245 KB), API upload (9) + manual (1 forbidden error on Jb9l1tT95ok)
- **Videos updated:**

| Video ID | Title | Impressions | CTR Before | Text on Thumbnail |
|----------|-------|-------------|------------|-------------------|
| rjtM2N5MIGM | Christ Will Destroy Edom — Genesis 49 | 16,391 | 7.84% | EDOM WILL FALL |
| Jb9l1tT95ok | The Most High Chosen People Official Movie | 7,737 | 2.62% | CHOSEN PEOPLE |
| qUNz7fKwtMo | Why Black Nobility Matters in These Last Days | 7,140 | 3.67% | BLACK ROYALTY |
| W8gbSwHzxKE | Top Ten Scriptures They Don't Teach in Church | 7,066 | 4.71% | HIDDEN SCRIPTURES |
| zZ2JGBR8kdI | The Only True High Holy Days Of The Bible | 6,522 | 3.65% | TRUE HOLY DAYS |
| KVbj6CvMX5c | Secrets Behind the King James Bible! | 6,357 | 3.49% | KJV SECRETS |
| MFTYh87UX00 | The Most High Chosen People | 6,073 | 4.76% | HIS PEOPLE |
| uGkJtkdElcg | The King James Revelation: Truth in These Last Days | 5,963 | 4.16% | KJV TRUTH |
| W0_WDcr0TFI | Ancient Black Hebrew Israelites Journey | 5,786 | 2.70% | ANCIENT JOURNEY |
| 9L5mYYDAF1o | Did King James Really Change Britain Forever? | 4,980 | 3.45% | KING JAMES |

- **Quota cost:** 450 units (1 uploaded manually)

#### Summary — March 17, 2026
| Action | Count |
|--------|-------|
| Part titles renamed to standalone | 84 (58 + 26) |
| Part numbers moved to descriptions | 84 |
| Broken em dashes fixed | 50 |
| Channel banner updated | 1 |
| Profile picture updated | 1 |
| Custom thumbnails uploaded | 20 (batch 1: 10, batch 2: 10) |
| Reassigned Short thumbnails to long-form | 4 |
| Competitor analysis doc created | 1 |
| Tribe playlists created | 2 (Judah: 10, Benjamin: 5) — quota hit, rest tomorrow |

---

### March 18, 2026 — Phase 4A: Playlists Complete

#### 11. Finished all 14 tribe/topic playlists
- **New playlists created:** 11 (+ 1 Benjamin video added + 2 from March 17)
- **Total:** 14 playlists, 104 videos organized by tribe/topic
- **Quota cost:** ~5,750 units
- **Playlists:**

| Playlist | Videos |
|----------|--------|
| The Tribe of Judah — Lions of Israel | 10 |
| The Tribe of Benjamin — Wolves of the Last Days | 6 |
| The Tribe of Ephraim — Fruitful in a Strange Land | 11 |
| The Tribe of Naphtali — A Hind Let Loose | 7 |
| The Tribes of Zebulun & Issachar — Mayans and Aztecs | 7 |
| The Tribe of Gad — Native Nations of Israel | 3 |
| The Tribe of Reuben — Nomadic Warriors | 2 |
| The Tribe of Asher — Mighty Warriors | 4 |
| The Tribes of Simeon & Levi — Divided in Israel | 4 |
| The Tribe of Dan — Judging His People | 1 |
| The Lost Tribes of Israel — Where Did They Go? | 14 |
| Deuteronomy 28 — Curses & Prophecy Fulfilled | 14 |
| 12 Tribes of Israel — The Big Picture | 36 |

- **Why:** "Part 1-80" playlists don't help discovery. Tribe-based playlists let new viewers binge their topic of interest
- **Expected impact:** Increased session duration, better recommendations, viewers binge-watching by tribe

#### 10. Channel trailer script prepared
- **Script:** 2:30 cinematic trailer covering all major tribes, Deuteronomy 28, and call to subscribe
- **Title:** "The 12 Tribes of Israel — Who They REALLY Are and Where They Went (FULL Breakdown)"
- **Status:** Script ready, Tommy converting to video with biblical video conversion system
- **Next:** Upload as unlisted, set as channel trailer for non-subscribers

---

### March 24, 2026 — 1 Week Post-Optimization Check-In (Live API Pull)

#### Live Channel Metrics

| Metric | Baseline (Mar 16) | Live (Mar 24) | Change |
|--------|-------------------|---------------|--------|
| Subscribers | 5,876 | 5,890 | **+14** |
| Total Views | 764,290 | 735,132 | -29,158 (expected — 30 deleted videos removed their view counts) |
| Total Videos | 238 | 245 | +7 new uploads since optimization |

#### Last 28 Days Analytics (Live)

| Metric | Value |
|--------|-------|
| Views | 14,301 |
| Watch Time (minutes) | 9,284 |
| Avg View Duration | 2:16 (136 sec) |
| Subscribers Gained | 151 |
| Subscribers Lost | 20 |
| **Net Subscribers** | **+131** |
| Likes | 816 |
| Comments | 25 |

#### Recent Upload Performance (Mar 15–24)

| Date | Views | Likes | Title |
|------|-------|-------|-------|
| Mar 22 | 987 | 45 | The Real Gospel Message About Defilement |
| Mar 21 | 144 | 2 | The 12 Tribes of Israel — Hidden Knowledge in Scripture |
| Mar 21 | 80 | 7 | Reading The Bible With NEW EYES in 2026 |
| Mar 19 | 35 | 1 | Ancient Wisdom the World Forgot About Israel |
| Mar 18 | 79 | 2 | Who Really Are the 12 Tribes? The Answer Changes Everything |
| Mar 18 | 100 | 6 | The 12 Tribes of Israel — Who They REALLY Are |
| Mar 17 | 61 | 3 | The Hidden Truth About Who Israel Really Is |
| Mar 16 | 72 | 1 | Who Inherited the Promise? The 12 Tribes of Israel |
| Mar 15 | 125 | 5 | Who Really Are the 12 Tribes of Israel Today? |
| Mar 15 | 54 | 1 | The Family Jesus Chose Over His Own |

#### Assessment

- **Cleanup worked:** Channel deleted 30 low-quality videos but sub growth stayed healthy (+131 net in 28 days)
- **View count drop is cosmetic:** Lost 29K total views because deleted videos' counts were removed — no actual traffic loss
- **Mar 22 upload is a standout:** 987 views + 45 likes in 2 days = 4.5% like rate, strong engagement signal
- **Most new uploads underperforming (35-144 views):** Algorithm likely still recalibrating after bulk metadata changes. Expected — takes 2-4 weeks to normalize.
- **Avg view duration of 2:16 is strong** for a Shorts-heavy channel
- **Next milestone:** Export fresh YouTube Studio CSVs on April 7 for proper CTR/impression before-and-after comparison

---

### April 17, 2026 — Meta App Review: Root Cause Found & Fixed

#### Root cause of 0/1 test calls (2+ weeks stuck)
Three separate bugs caused every previous attempt to fail:

1. **Wrong API (April 2–13):** All test calls used `graph.facebook.com` with the Facebook app (`META_APP_ID: 1452257036358754`). The `instagram_business_*` permissions require `graph.instagram.com` with the Instagram app (`IG_APP_ID: 922450807234394`). Scripts affected: `meta-test-calls.py`, `meta-app-review.py`, Graph API Explorer calls.

2. **Wrong content_publish call (April 15–17):** `meta-ig-business-review.py` (correct API) only called `GET /content_publishing_limit` — a read. Meta requires `POST /{ig-user-id}/media` (container creation) to count as a content_publish test call.

3. **Wrong insights metric (April 15–17):** Script passed `impressions` as a metric to `GET /{ig-user-id}/insights`. The Instagram Business Login API does NOT support `impressions` at account level — valid metrics are: `reach`, `follower_count`, `website_clicks`, `profile_views`, `online_followers`. This call returned an error on every run. Meta can't count a failed call.

#### Fixes applied
- `meta-ig-business-review.py`: API version bumped v21.0 → v22.0
- Added `POST /{ig-user-id}/media` for content_publish (creates container, never publishes)
- Fixed insights metrics: `impressions,reach,profile_views` → `reach,follower_count,profile_views`
- Added media-level insights: `reach,saved,likes,comments,shares`
- Added comment replies endpoint as belt-and-suspenders for manage_comments
- Added `--token` flag for dashboard-generated tokens

#### Successful run — April 17, 2026 ~4:00 PM ET
All 5/5 test calls returned OK for the first time:
- `GET /me` → OK (@aibiblegospels, id=26231113889873297)
- `POST /26231113889873297/media` → OK (container created)
- `GET /17908663431203537/comments` → OK (1 comment)
- `GET /26231113889873297/insights?metric=reach,follower_count,profile_views` → OK (real data returned)
- `GET /26231113889873297/conversations` → OK (25 threads)

#### Timeline
- **April 17 ~4:00 PM ET** — All 5/5 test calls succeeded
- **April 17 ~4:30 PM ET** — `content_publish` already showed "Completed" (green dot) in dashboard
- **April 17 ~5:00 PM ET** — App Review SUBMITTED. All sections green. Status: "Review in progress"
  - All 6 permissions submitted: Human Agent, instagram_business_basic, instagram_business_manage_messages, instagram_business_content_publish, instagram_business_manage_insights, instagram_business_manage_comments
  - Meta says: "Most submissions are reviewed within 10 days"
- **API access confirmed during review** — `GET /me/media` returns posts via graph.instagram.com with IG_BUSINESS_TOKEN
- **Waiting for:** Approval (1-10 business days, expected by April 28)
- **Once approved:** Run `python scripts/meta-update-posts.py instagram --live` to fix all 538 IG captions

---

### April 3-4, 2026 — New PC Setup + Meta App Review + Caption Fix

#### New PC Migration
- Rebuilt codebase on new Windows 11 PC
- Repopulated .env with Meta credentials (retrieved Page ID + IG Business ID via API since they weren't on flash drive)
- **Page ID:** 601690023018873 | **IG Business ID:** 17841454335324028

#### Repurpose.io AI Caption Bug — Fixed Across All Platforms
- **Root cause:** "AI auto-generate captions" was enabled on all 4 workflows during April 1 setup — appended generic off-brand AI text to every post
- **Fix:** Disabled AI auto-generate on all 4 workflows
- **Facebook:** 1 post fixed via API (`scripts/fix-facebook-captions.py`) — script scans all posts, strips garbage at known markers, updates via Graph API
- **TikTok / X / Instagram:** Fixed manually
- **New script created:** `scripts/fix-facebook-captions.py` — reusable for future garbage detection

#### Meta App Review — Re-submitted with Expanded Permissions
- **Previous submission:** instagram_business_basic + instagram_business_manage_comments only
- **New submission:** Added instagram_business_content_publish, instagram_business_manage_messages, Human Agent
- **Site URL fixed:** Was pointing to bornmadebossesapparel.com → corrected to youtube.com/@AIBIBLEGOSPELS
- **API test calls made** via Graph API Explorer:
  - `GET /17841454335324028/media` (registers instagram_manage_comments)
  - `GET /17841454335324028/content_publishing_limit?fields=config,quota_usage` (registers instagram_content_publish)
- **Status:** Waiting up to 24hrs for test calls to show as 1/1 → then Submit → 1-5 day review
- **Once approved:** Run `python scripts/meta-update-posts.py instagram --live` to fix all 538 IG captions

---

### March 30, 2026 — Phase 4B + YouTube Title Rewrite

#### 12. Rewrote 15 YouTube video titles for viral hooks
- **Videos affected:** 15 (mix of long-form and Shorts)
- **Method:** Analyzed top-performing title patterns from competitors (ForbiddenGospel, GodsWordUnmasked, The Bible in Black). Applied identity-driven, curiosity-gap, and prophecy-reveal formulas.
- **Why:** Channel CTR at 4.06% vs target of 6-10%. Stronger title hooks = more clicks from impressions already being served.
- **Expected impact:** +1-2% CTR improvement on rewritten videos

#### 13. Phase 4B — Pillar video script written
- **Script:** Long-form animated explainer (10-20 min) covering full 12 Tribes identity breakdown
- **Status:** Script ready. Tommy converting to video with Kling AI + CapCut workflow.
- **Why:** Channel needs 4-6 long-form videos for ad revenue eligibility and evergreen search traffic

---

### April 1-2, 2026 — Phase 5: Social Media Automation

#### 14. Facebook — 8 viral posts live via API
- **Script:** `scripts/facebook-post.py`
- **Posts live:** identity, prophecy, identity_chart, suppressed_truth, awe, tribe_engagement, cinematic, current_events
- **Method:** Meta Graph API v25.0. YouTube link posted as first comment (avoids Facebook reach penalty on link-in-body).
- **App:** Meta developer app published (App ID: 1452257036358754)
- **Expected impact:** Cross-platform reach, driving Facebook audience to YouTube

#### 15. Repurpose.io — All 4 platform workflows configured
- **Platforms:** Instagram, TikTok, X/Twitter, Facebook
- **Caption templates:** Platform-specific viral templates added to each workflow (see `docs/repurpose-templates.md`)
- **First comment (YouTube link):** Enabled on all 4 workflows
- **AI auto-generate captions:** Enabled on all 4 workflows
- **TikTok posting frequency:** Bumped to 3 posts/day
- **Why:** 228-video Google Drive backlog needed automated distribution system. Repurpose handles all 4 platforms at 9am and 6pm daily.

#### 16. All 4 platform bios updated
- **Platforms:** Facebook, TikTok, Instagram, X/Twitter
- **Copy:** Niche identity + YouTube funnel CTA on every bio. Character-counted templates in `docs/repurpose-templates.md`.

#### 17. Meta App Review submitted
- **Permissions requested:** instagram_business_basic, instagram_business_manage_comments
- **Date submitted:** April 2, 2026
- **Why:** Required to edit captions on existing 538 Instagram posts. App was in Development mode — could only manage own account. Business mode requires App Review.
- **Status:** Pending approval (1-5 business days)
- **Next action:** Once approved → run `python scripts/meta-update-posts.py instagram --live`

#### 18. YouTube OAuth token refreshed
- **Date:** April 1, 2026
- **Method:** Deleted expired token.json → ran `python scripts/connect.py` → browser OAuth flow
- **Why:** token.json had expired (invalid_grant error on channel-status.py)

#### 19. X/Twitter API — blocked by Free tier
- **Keys saved:** Consumer Key, Secret, Access Token, Access Secret (in .env)
- **Script built:** `scripts/twitter-post.py` — 8 viral tweet templates ready
- **Status:** X Free/Pay-per-use tier does NOT support OAuth 1.0a posting
- **Workaround:** Repurpose.io handles X posting. Script ready for if/when upgraded to X Basic ($100/mo).

#### Summary — April 1-2, 2026
| Action | Result |
|--------|--------|
| Facebook posts live | 8/8 ✅ |
| Repurpose workflows configured | 4/4 ✅ |
| Platform bios updated | 4/4 ✅ |
| YouTube titles rewritten | 15 ✅ |
| Meta App Review submitted | ✅ (pending approval) |
| Instagram caption updates (538 posts) | ⏳ Blocked — pending App Review |
| X/Twitter API posting | ❌ Free tier limitation |

---

### April 3, 2026 — Repurpose.io AI Caption Fix

#### Fix: Disabled AI auto-generate captions on all 4 Repurpose workflows
- **Problem:** Repurpose.io's "AI auto-generate captions" feature was appending generic AI-generated promotional text after every caption template on all platforms. Posts showed the correct branded caption followed by completely off-niche filler (travel content, wellness text, startup promotional copy, and literal LLM meta-responses like "Sure! Here's a TikTok-optimized version of your post:").
- **Root cause:** Feature was enabled during April 1 workflow setup under the assumption it would enhance per-video captions. In practice, Repurpose's AI has no niche context and generates generic promotional content that has nothing to do with the channel.
- **Fix:** Disabled "AI auto-generate captions" in all 4 Repurpose workflows (Instagram, TikTok, X/Twitter, Facebook)
- **Platforms affected:** All 4 — confirmed live on Facebook, TikTok, X, and Instagram
- **Fix applied per platform:**
  - Facebook: 1 post fixed via API (`scripts/fix-facebook-captions.py`) — 39 other posts were already clean
  - TikTok: Fixed manually
  - X/Twitter: Fixed manually
  - Instagram: Fixed manually
- **Going forward:** Caption templates in `docs/repurpose-templates.md` are the sole caption source. No AI appending.
- **Lesson:** Hand-written niche templates outperform generic AI. AI generate stays off permanently.

---

### April 2, 2026 — Long-Form Video Tag & Title Fixes

#### 20. Fixed tags and titles on 5 long-form videos
- **Problem:** 5 long-form videos had `shorts` in their tags + completely off-niche tags (healing music, psalm 91, soaking worship music). YouTube was mis-categorizing these and serving them to the wrong audience.
- **Videos fixed:**
  - `mAJS97kNC5E` — Title typo fixed: "Reveled" → "Revealed" + 23 niche tags applied
  - `xL8v7eZ9mwc` — Replaced generic tags with 23 niche + audiobook-specific tags
  - `dpERIR0YZZ8` — Replaced generic tags with 22 niche + Deut 28 discovery tags
  - `DIvHY0Ic1Ac` — Removed @AIBIBLEGOSPELS from title + 22 niche tags
  - `rKLtGlKw4ak` — Replaced generic tags with 22 niche + kingdom/commands tags
- **New tag set (all 5):** 12 tribes of israel, hebrew israelites, black hebrew israelites, lost tribes of israel, israelite awakening, deuteronomy 28, bible prophecy, biblical truth, end times prophecy, bible study, king james bible, kjv 1611, ai bible gospels, israel identity, chosen people of god, gospel truth, hidden history + video-specific extras
- **Expected impact:** Algorithm now properly categorizes these as long-form 12 Tribes content. Should start surfacing in search and suggested for the right audience within 1-2 weeks.
- **Also done:** X profile name fixed — "Bible Gospels" → "AI Bible Gospels"

#### 21. Channel About description rewritten
- **Problem:** Old description was generic — first 150 chars said nothing niche-specific. No searchable keywords in the body. No CTA or links.
- **Fix:** Rewrote to lead with "12 Tribes of Israel Revealed" in the first line (what shows in YouTube search). Added Hebrew Israelites, Deuteronomy 28, Black Hebrew Israelites, lost tribes, KJV naturally in the body. Added subscriber CTA with social proof (5,900+).
- **Expected impact:** Better channel discovery when users search Hebrew Israelite / 12 Tribes terms. Higher subscribe conversion from channel page visits.

---

## Upcoming Changes

### Pending Approval (1-5 business days)
- Meta App Review → run `python scripts/meta-update-posts.py instagram --live` to fix all 538 Instagram post captions

### Son's Task
- Create `New-Shorts\` subfolder in `G:\My Drive\AI BIBLE GOSPELS\Videos\`
- Create 4 new Repurpose workflows (IG, TikTok, X, FB) pointing to `New-Shorts\` folder
- All new Shorts go into `New-Shorts\` going forward; existing 228-video backlog workflows run untouched

### When TikTok hits 1,000 followers (currently 470)
- Add YouTube channel link to TikTok bio

### This Month
- Apply for TikTok API at developers.tiktok.com
- Refresh Meta token every 60 days (developers.facebook.com/tools/debug/accesstoken)
- Fix X profile name: "Bible Gospels" → "AI Bible Gospels"

### Future — Content Strategy
- Develop 4-6 long-form animated explainers (10-20 min) for ad revenue + evergreen search
- Apply for YouTube monetization once long-form content is live
- Add optimized descriptions to all Shorts via API

---

### April 18, 2026 — 1-Month Checkpoint Run (during YPP suspension)

Ran [scripts/checkpoint-1month.py](../scripts/checkpoint-1month.py) for the 28-day window 2026-03-21 to 2026-04-18.

**Channel totals (28d):**
- Views: 6,379 (~228/day — flat)
- Watch time: 7,476 min / 124 hrs
- Avg view duration: **146 sec (2:26)** — strong retention signal
- Net subs: **+41** (53 gained, 12 lost)
- Likes: 266 / Shares: 64 / Comments: 9

**Per-video baseline diff:** Top 15 videos all show +0.0% to +0.5% growth vs the March 16 baseline. The viral 12 Tribes Origins Short (115K views) added only +576 views in a full month — back in its peak it did that in a day.

**Diagnosis:** The YPP suspension is choking reach across all videos. Views are flatlined because search/suggested/browse traffic is gated. This means **the impact of title + thumbnail optimization cannot be measured under current conditions** — reach is near-zero.

**Silver linings:**
- 146s avg view duration confirms content quality is unaffected
- +41 net subs/month with ~0 reach = the small trickle of viewers converts well

**Action:** Treat this as the "during-suspension baseline." Re-run checkpoint **~2 weeks after YPP appeal resolves** (appeal due 2026-04-30 → earliest clean re-measurement 2026-05-14).

**Snapshot saved to:** `analytics/checkpoint-2026-04-18/`

---

### April 18, 2026 — TikTok Content Posting API submitted for review

- **App**: Ai-Bible-Gospels (Organization: Born Made Bosses LLC)
- **Products**: Login Kit + Content Posting API (drafts/inbox mode; Direct Post OFF)
- **Scopes**: `user.info.basic` + `video.upload`
- **Target user (sandbox)**: `aibiblegospels_`
- **Redirect URI**: `https://12tribesofisrael.github.io/aibiblegospels-legal/callback.html` (public forwarder — TikTok rejects localhost)
- **Script**: [scripts/tiktok-post.py](../scripts/tiktok-post.py) — OAuth + chunked upload + status polling
- **Proof**: 2 test uploads succeeded end-to-end (9.7MB video accepted, `publish_id` returned, status polling confirmed)
- **Demo video**: recorded via OBS, uploaded to the form, submitted 2026-04-18
- **Legal site**: live at `https://12tribesofisrael.github.io/aibiblegospels-legal/` (separate repo `12TribesofIsrael/aibiblegospels-legal` — ToS + Privacy + OAuth callback forwarder + TikTok URL verification file)
- **Why**: Enables cross-posting Shorts from the content pipeline directly to TikTok without manual file transfer
- **Gotchas documented**: TikTok rejects localhost redirects (unlike Meta); unreviewed production creds fail OAuth (use Sandbox + Target User first); save is blocked without a placeholder demo video
- **Status**: Awaiting TikTok review verdict

---

## Analytics Checkpoints

Use these dates to measure impact in YouTube Studio:

| Checkpoint | Date | What to Compare |
|------------|------|-----------------|
| Pre-optimization baseline | March 16, 2026 | Snapshot above |
| 1 week post-cleanup | March 23, 2026 | CTR, impressions, avg views |
| 2 weeks post-cleanup | March 30, 2026 | CTR trend, sub growth rate |
| 1 month post-cleanup | April 16, 2026 | Full impact assessment |
| Post title-rename (1 week) | March 24, 2026 | Search traffic, CTR on renamed videos |
| Post title-rename (1 month) | April 17, 2026 | Search impressions, new viewer % |
| Post thumbnail batch 1 (1 week) | March 24, 2026 | CTR on 10 updated videos |
| Post thumbnail batch 1 (1 month) | April 17, 2026 | CTR trend, view count changes |
