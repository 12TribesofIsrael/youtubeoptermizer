---
name: Meta App Review APPROVED — IG Business scopes live
description: App Review APPROVED & live as of 2026-04-27. All 5 advanced IG Business scopes pass production probes; live caption update returned success=true.
type: project
originSessionId: bcd90f81-62ce-4cfd-9853-eea2d174964b
---
Meta App Review for Instagram Business Login — **APPROVED & LIVE confirmed 2026-04-27**.

Submitted 2026-04-17 (after fixing 3 bugs: wrong API graph.facebook.com→graph.instagram.com, wrong content_publish call GET→POST, wrong insights metric impressions→reach/follower_count/profile_views). Approval landed within Meta's 10-day window.

## Verified live on 2026-04-27 (via scripts/meta-priv-probe.py + caption update probe)

All 5 advanced scopes pass on `graph.instagram.com/v23.0` with IG_BUSINESS_TOKEN:
- `instagram_business_basic` — `/me`, `/{ig_id}/media` return data
- `instagram_business_manage_comments` — `/{post_id}/comments` returned 1 comment
- `instagram_business_manage_insights` — `/{ig_id}/insights?metric=reach,follower_count,profile_views&period=day` returned values (e.g. reach 93/56)
- `instagram_business_manage_messages` — `/{ig_id}/conversations?platform=instagram` returned data
- `instagram_business_content_publish` — POST `/{ig_id}/media` created a container (auto-expires 24h)

End-to-end caption write also passes:
- POST to `/{media_id}` with `caption` + `comment_enabled=true` → `{"success":true}` HTTP 200
- IMPORTANT: caption updates require `comment_enabled` param — without it returns "The parameter comment_enabled is required" (IGApiException code 100). Update meta-update-posts.py if it doesn't already pass this.

## What's unlocked

- `python scripts/meta-update-posts.py instagram --live` — fix all 538 IG captions
- Comment moderation, DM management, content publish, and insights reads on @aibiblegospels

## Why

Needed to programmatically manage @aibiblegospels Instagram content (captions, comments, cross-posting, insights) — primary downstream use is the bulk caption/AEO rollout and DM auto-reply tooling.

## How to apply

Don't re-probe scopes — they're confirmed live. If a future call fails with a permissions error, re-test before assuming review status changed (token may have expired or specific endpoint may need different scope). Test with the meta-priv-probe.py harness first.
