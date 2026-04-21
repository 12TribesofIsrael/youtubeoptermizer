---
name: TikTok App Review status
description: REJECTED 2026-04-21 (2nd rejection — website URL, demo video, scopes). First rejection 2026-04-20 for name mismatch was fixed by renaming app to "AI Bible Gospels".
type: project
originSessionId: d6d44c50-a641-4f85-b422-6b0200ea977c
---
TikTok Content Posting API app review — **REJECTED twice**. Currently needs a third submission.

## Timeline

- **2026-04-18**: Original submission as "Ai-Bible-Gospels" for @aibiblegospels_.
- **2026-04-20**: First rejection — name mismatch. Reviewer flagged (1) app name different from website, (2) Privacy Policy didn't mention app by name, (3) Terms of Service didn't mention app by name. Root cause: TikTok app was "Ai-Bible-Gospels" but website (YouTube @AIBIBLEGOSPELS → "AI Bible Gospels"), Privacy Policy, and ToS all used "AI Bible Gospels". Fixed by renaming the TikTok app to "AI Bible Gospels" — no legal-page edits needed. Resubmitted same day.
- **2026-04-21**: Second rejection on the resubmitted version. Three new issues (below). Needs resubmit #3.

**Why:** Enables automated video draft uploads from the content pipeline to TikTok. Required for cross-posting the Shorts we already publish on YouTube + Meta.

**How to apply:** Don't touch the sandbox OAuth/upload flow — scripts/tiktok-post.py is proven working. Both rejections were about review-submission artifacts (naming, website, demo video, scope hygiene), not the integration itself.

## 2nd rejection reasons (verbatim from reviewer, 2026-04-21)

1. **Website URL** — cannot be a landing page or login page; must be an externally-facing, fully-developed website. If it is a login page, a test account must be provided in Apply Reason.
2. **Demo video** — must show complete end-to-end flow; must use sandbox (or mockup); every selected product and scope must be clearly demonstrated; current demo "does not provide enough clarity and context."
3. **Unused products/scopes** — must be removed before resubmit.

Likely root cause of #1: the submitted Website URL was the GitHub Pages legal/callback host (`12tribesofisrael.github.io/aibiblegospels-legal/`), which is a forwarder + legal pages, not a real site.

## Resubmit checklist (for 3rd submission)

- [ ] Stand up a real content/marketing website (About, What we do, Contact) — separate from the legal pages repo. Another GH Pages repo is fine if it has real content.
- [ ] Re-record sandbox demo narrating each scope as it's used: login (user.info.basic) → upload draft (video.upload) → confirm in inbox.
- [ ] Trim products/scopes to exactly what's demoed (currently user.info.basic + video.upload, Login Kit + Content Posting API).

## Key facts

- **App**: "AI Bible Gospels" (Organization: Born Made Bosses LLC) — renamed 2026-04-20 from "Ai-Bible-Gospels" to match website + legal pages
- **Sandbox tester**: aibiblegospels_ (added 2026-04-18 3:08 PM)
- **Active creds in .env**: SANDBOX (sbawswnygychzo38lw) — production creds preserved as comments
- **Scopes requested**: user.info.basic + video.upload (no video.publish — requires extra approval)
- **Products**: Login Kit + Content Posting API (Direct Post OFF, inbox/drafts only)
- **Redirect URI**: https://12tribesofisrael.github.io/aibiblegospels-legal/callback.html (keep as-is; it's the OAuth callback, not the Website URL)
- **Legal pages**: live at 12tribesofisrael/aibiblegospels-legal (separate repo)

## Proven working end-to-end (sandbox)

OAuth succeeded, 9.7MB video uploaded in one chunk, status polling confirmed via `/v2/post/publish/status/fetch/`. Two successful test uploads completed 2026-04-18.

## Gotchas learned

- TikTok **rejects localhost redirect URIs** on production Dev Portal (Meta allows it — TikTok does not). Must use a publicly-hosted forwarder.
- `callback.html` on GitHub Pages captures `?code=...` and `window.location.replace()` to localhost.
- Pre-approval OAuth **requires Sandbox mode** — production credentials return `client_key` error until the app is reviewed.
- Sandbox credentials are **separate** from Production — cloning Sandbox from Production copies config but not credentials.
- TikTok Dev Portal **won't let you save** the app config without a placeholder demo video uploaded — upload any video, save, then swap.
- Sandbox video processing is **slow** (5-15 min PROCESSING_UPLOAD → SEND_TO_USER_INBOX); production is <30s.
- **App name must match website + Privacy Policy + ToS exactly.** Rename the app, not the legal pages.
- **Website URL ≠ Redirect URI.** Website URL must be a real info site; reviewers reject GH-Pages-hosted legal/callback repos.
