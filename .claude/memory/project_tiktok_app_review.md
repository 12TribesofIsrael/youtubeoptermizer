---
name: TikTok App Review status
description: First submission 2026-04-18 rejected for name mismatch; resubmitted 2026-04-20 as "AI Bible Gospels" — awaiting verdict
type: project
originSessionId: 3f97120f-9e3e-4e35-89e8-cf5aa8126068
---
TikTok Content Posting API app review — **resubmitted 2026-04-20** after first-round rejection. App name is now **"AI Bible Gospels"** (spaces, no hyphens) — previously "Ai-Bible-Gospels".

**Rejection (2026-04-20)**: reviewer flagged (1) app name different from website, (2) Privacy Policy does not mention app by name, (3) Terms of Service does not mention app by name. Root cause was a single naming mismatch: TikTok app was "Ai-Bible-Gospels" but the website (YouTube @AIBIBLEGOSPELS → "AI Bible Gospels"), Privacy Policy, and ToS all used "AI Bible Gospels". Fixed by renaming the TikTok app to match — no legal-page edits needed.

**Original submission:** 2026-04-18 for @aibiblegospels_.

**Why:** Enables automated video draft uploads from the content pipeline to TikTok. Required for cross-posting the Shorts we already publish on YouTube + Meta.

**How to apply:** Don't rebuild the OAuth/upload flow — scripts/tiktok-post.py is working. If Meta's pattern holds, expect a ~24-72h turnaround; watch for rejection reasons (common TikTok rejection triggers: demo video missing a scope, domain mismatch, explanation too vague about first-party use).

## Key facts

- **App**: "AI Bible Gospels" (Organization: Born Made Bosses LLC) — originally "Ai-Bible-Gospels", renamed 2026-04-20 to match website + legal pages
- **Target user** (sandbox tester): aibiblegospels_ (added 2026-04-18 3:08 PM)
- **Active credentials in .env**: SANDBOX (sbawswnygychzo38lw) — production creds preserved as comments
- **Scopes requested**: user.info.basic + video.upload (no video.publish — requires extra approval)
- **Products**: Login Kit + Content Posting API (Direct Post OFF, inbox/drafts only)
- **Redirect URI**: https://12tribesofisrael.github.io/aibiblegospels-legal/callback.html
- **Legal pages**: live at 12tribesofisrael/aibiblegospels-legal (separate repo)

## Proven working end-to-end

OAuth succeeded, 9.7MB video uploaded to TikTok servers in one chunk, status polling confirmed via `/v2/post/publish/status/fetch/`. Two successful test uploads completed 2026-04-18 — one pre-submission rehearsal + one during demo recording.

## Gotchas learned

- TikTok **rejects localhost redirect URIs** on the production Dev Portal (Meta allows it — TikTok does not). Must use a publicly-hosted page that forwards the code.
- `callback.html` on GitHub Pages does the forward: captures `?code=...` from TikTok and `window.location.replace()` to `https://localhost:9876/callback?code=...`.
- Pre-approval OAuth requires **Sandbox mode** — production credentials return `client_key` error until the app is reviewed.
- Sandbox credentials are **separate** from Production — cloning Sandbox from Production copies config but not credentials.
- TikTok Dev Portal **won't let you save** the app config without a placeholder demo video uploaded — chicken-and-egg. Upload any video as a placeholder, save, then swap in the real demo later.
- Sandbox video processing is **slow** (5-15 min for PROCESSING_UPLOAD → SEND_TO_USER_INBOX); production is <30s.
