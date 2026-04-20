---
name: TikTok app-approval probes — false positives vs real signal
description: Only the post-login consent step reveals pre-approval client_key error; client_credentials grant + authorize URL redirect are both false positives
type: feedback
originSessionId: 7318559c-cd18-43ae-8402-d813b2cf598f
---
When checking whether a TikTok app has passed review, **do not rely on these signals** — they succeed even for unreviewed apps:

1. `client_credentials` grant at `/v2/oauth/token/` — returns a valid `clt.*` token for any registered app regardless of review state.
2. GET on `/v2/auth/authorize/?client_key=<prod>` — 302 redirects to `tiktok.com/login?enter_from=dev_<client_key>` for both approved and unapproved apps.

**The only definitive automated probe** is to complete the OAuth flow past the TikTok user login. An unreviewed app shows a "Something went wrong — client_key" error page immediately after successful login. An approved app shows the app-consent screen with scopes + branding.

**Why:** TikTok enforces the review gate at the consent-screen step, not at authorize-URL generation or client_credentials. The authorize URL accepts any syntactically-valid registered client_key regardless of scope approval.

**How to apply:**
- For automated approval checks, completing a full browser login is required — there is no shortcut API.
- When the `client_key` error appears post-login, it's the approval gate, not a config bug — don't chase app settings.
- Learned 2026-04-20 probing the Ai-Bible-Gospels app (submitted 2026-04-18). client_credentials + authorize redirect both succeeded, but post-login showed the client_key error — app was still in review.
