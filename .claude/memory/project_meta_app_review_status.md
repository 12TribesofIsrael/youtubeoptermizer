---
name: Meta App Review submitted — awaiting approval
description: App Review SUBMITTED 2026-04-17 after fixing 3 bugs (wrong API, wrong POST, wrong metrics). Review in progress, expect approval by 2026-04-28.
type: project
originSessionId: bcd90f81-62ce-4cfd-9853-eea2d174964b
---
Meta App Review for Instagram Business Login was **SUBMITTED on 2026-04-17**.

**Status:** Review in progress. Meta says "most submissions reviewed within 10 days" — expect by 2026-04-28.

**Permissions submitted:** Human Agent, instagram_business_basic, instagram_business_manage_messages, instagram_business_content_publish, instagram_business_manage_insights, instagram_business_manage_comments

**What was fixed on 2026-04-17 (after 2+ weeks stuck at 0/1):**
1. Wrong API: old scripts used graph.facebook.com — fixed to graph.instagram.com
2. Wrong content_publish call: was GET /content_publishing_limit — fixed to POST /media (container)
3. Wrong insights metric: "impressions" invalid on IG Business API — fixed to reach, follower_count, profile_views

**API access works during review** — IG_BUSINESS_TOKEN can already read posts via graph.instagram.com.

**Once approved:** Run `python scripts/meta-update-posts.py instagram --live` to fix all 538 IG captions.

**Why:** Needed to programmatically manage @aibiblegospels Instagram content (captions, comments, cross-posting).
