---
name: IG Business API metrics differ from Facebook API
description: Instagram Business Login API (graph.instagram.com) does NOT support "impressions" metric at account level — use reach, follower_count, profile_views instead. Media-level uses reach, saved, likes, comments, shares (not impressions for all types).
type: feedback
originSessionId: bcd90f81-62ce-4cfd-9853-eea2d174964b
---
The Instagram Business Login API (graph.instagram.com) has DIFFERENT valid metrics than the old Facebook-based Instagram API (graph.facebook.com).

**Account-level valid metrics:** reach, follower_count, website_clicks, profile_views, online_followers
**Account-level INVALID:** impressions (causes API error)

**Media-level valid metrics:** reach, saved, likes, comments, shares
**Media-level INVALID:** impressions (not supported for all media product types)

**Why:** The meta-ig-business-review.py script was passing `impressions` as a metric, which returned an error. The script reported FAIL but we kept re-running without reading the actual error output. This caused instagram_business_manage_insights to stay at 0/1 in App Review for weeks.

**How to apply:** When building IG Business Login API calls, always use the metrics listed above. Never copy metrics from graph.facebook.com code — they are different APIs with different schemas.
