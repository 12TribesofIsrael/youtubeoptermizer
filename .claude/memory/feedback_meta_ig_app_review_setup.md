---
name: Meta Instagram App Review — correct OAuth flow
description: How to register instagram_business_* API test calls toward Meta App Review (uses separate IG app, not FB app, via graph.instagram.com)
type: feedback
originSessionId: 1b4b683e-8aa7-4b87-bd97-c88c9db79096
---
To register test calls against the `instagram_business_*` permissions (basic, content_publish, manage_comments, manage_insights, manage_messages), you MUST use the **Instagram API with Instagram Login** flow — NOT the Facebook Login flow.

**Why:** Meta has two parallel sets of Instagram permissions:
- Old: `instagram_basic`, `instagram_content_publish`, `instagram_manage_comments` — granted via Facebook Login, tokens work against `graph.facebook.com`. The existing `scripts/meta-app-review.py` and `scripts/meta-test-calls.py` only exercise these.
- New: `instagram_business_*` — granted via Instagram Business Login, tokens work against `graph.instagram.com`. App Review requires test calls against THESE.

Using a Facebook-Login-derived token against `graph.facebook.com/{ig-id}/media` registers calls for the OLD permissions, which is why they showed "Completed" while the new ones stayed at 0/1.

**How to apply:**
- Working script: `scripts/meta-ig-business-review.py` (run it when new IG scopes need test calls)
- Uses separate credentials: `IG_APP_ID` + `IG_APP_SECRET` in `.env` (distinct from `META_APP_ID` / `META_APP_SECRET` which are the Facebook app)
- IG app ID: `922450807234394`. Facebook app ID: `1452257036358754`. Different apps.
- Redirect URI must be HTTPS; `https://localhost:9876/callback` works with a self-signed cert (the script generates one to `~/.meta-ig-review-cert/`)
- Register the redirect URI under: Meta Dashboard → Use cases → "Manage messaging & content on Instagram" → API setup with Instagram login → section 4 "Set up Instagram business login"
- Re-run test calls without re-authing: `python scripts/meta-ig-business-review.py --reuse`
- `IG_BUSINESS_TOKEN` is saved to `.env`, long-lived (~60 days)
