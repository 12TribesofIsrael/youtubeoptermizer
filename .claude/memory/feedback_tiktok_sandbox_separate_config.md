---
name: TikTok dev portal — Sandbox vs Production are separate configs
description: TikTok sandbox has its own redirect URIs / scope / description / demo video config; saving in the main app config does NOT propagate to sandbox; must edit each separately
type: feedback
---
TikTok dev portal splits each app into two parallel config spaces — a **Production** app (what gets reviewed and serves the prod `client_key`) and one or more **Sandboxes** (each with its own `sb...`-prefixed `client_key`). They have separate redirect URI lists, scope configs, descriptions, and demo videos.

**Why:** On 2026-05-01, after building the multi-tenant OAuth flow on aibiblegospels.com, OAuth via the sandbox client_key kept rejecting with `redirect_uri` error even after adding the new URI to what looked like the main app config. The fix was finding the sandbox section (signaled by a "Delete Sandbox" button in the header) and adding the URI there too.

**How to apply:**
- When testing OAuth via the `sb...` client_key → the sandbox config is what's being read; save changes there.
- When submitting for review → the production config is what TikTok evaluates; sandbox edits don't affect review.
- After save in either config, propagation takes seconds — if OAuth still rejects after 30s+, you're editing the wrong tier.
- Sandbox supports up to 10 redirect URIs — register both the website OAuth URI and any script-OAuth URIs (e.g., GH Pages forwarder for `tiktok-post.py`) in the same sandbox so both flows work.
- "Submit for review" is a production-only action; never needed to make sandbox edits live.
