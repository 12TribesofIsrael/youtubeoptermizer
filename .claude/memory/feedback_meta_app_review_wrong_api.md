---
name: Meta App Review — instagram_business_* needs graph.instagram.com not graph.facebook.com
description: instagram_business_* permissions require Instagram Business Login API (graph.instagram.com + IG_APP_ID), NOT the old Facebook API (graph.facebook.com + META_APP_ID). Test calls against the wrong API will never register.
type: feedback
originSessionId: bcd90f81-62ce-4cfd-9853-eea2d174964b
---
The first ~10 attempts to register Meta App Review test calls failed because they used the WRONG API:

- **Wrong:** graph.facebook.com with META_APP_ID (1452257036358754) and META_ACCESS_TOKEN — this is for the OLD permissions (instagram_basic, instagram_manage_comments, instagram_content_publish)
- **Correct:** graph.instagram.com with IG_APP_ID (922450807234394) and IG_BUSINESS_TOKEN — this is for the NEW permissions (instagram_business_basic, instagram_business_manage_comments, etc.)

Scripts that use the wrong API: meta-test-calls.py, meta-app-review.py
Script that uses the correct API: meta-ig-business-review.py

**Why:** Wasted 2+ weeks (April 2–17) running test calls against the wrong endpoint. Calls succeeded functionally but Meta's review system didn't count them.

**How to apply:** For any future instagram_business_* work, always use graph.instagram.com with IG_APP_ID credentials. Never use graph.facebook.com for these permissions. The content_publish permission also requires a POST /media call (container creation), not just GET /content_publishing_limit.
