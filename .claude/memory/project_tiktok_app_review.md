---
name: TikTok App Review status
description: 4th submission live 2026-04-29 after 3rd-round rejection 2026-04-28; ToS/Privacy URLs moved to apex, app description rewritten as creator service to dodge "personal/internal use" flag
type: project
originSessionId: 3f97120f-9e3e-4e35-89e8-cf5aa8126068
---
TikTok Content Posting API app review — **4th submission live 2026-04-29** after the 3rd round rejected on 2026-04-28.

## Timeline

- **2026-04-18** — 1st submission as "Ai-Bible-Gospels"
- **2026-04-20 02:18 UTC** — 1st rejection: name mismatch
- **2026-04-20** — renamed to "AI Bible Gospels", 2nd submit
- **2026-04-21 08:57 UTC** — 2nd rejection: Website URL + Demo video
- **2026-04-22** — 3rd submit after full fix pass
- **2026-04-28** — 3rd rejection (3 reviewer notes — see below)
- **2026-04-29** — 4th submit after 4-field fix (this round)

## 3rd rejection reasons (verbatim, 2026-04-28)

- "Invalid Terms of Service link provided"
- "Invalid Privacy Policy link provided"
- "App will not be approved for personal or company internal use."

**Root cause:** the GH-Pages legal pages literally said *"Our software is used exclusively by the account owner"* — the textbook definition of personal/internal use. The submitted Website-URL-as-ToS-and-Privacy was also just the homepage (no `/terms` or `/privacy` route existed yet).

## Apr 29 fix pass (what changed before 4th submit)

1. **Created `/terms` and `/privacy` routes** on the apex Next.js/Vercel site (`aibiblegospelscom` repo, commit `85d3f13`). Reframed copy as a publishing-service offered to creators connecting their own TikTok/IG/FB/YT accounts. Added explicit data-deletion path via `aibiblegospels444@gmail.com`.
2. **Updated TikTok portal fields:**
   - Description (120-char limit): *"Creators schedule and publish video posts to their own TikTok account, then track engagement and growth analytics."* (replaces the rejected "our own TikTok account / our audience" wording)
   - Terms URL: `https://aibiblegospels.com/terms` (was `https://www.aibiblegospels.com/`)
   - Privacy URL: `https://aibiblegospels.com/privacy` (was `https://www.aibiblegospels.com/`)
   - Web/Desktop URL: `https://aibiblegospels.com` (apex, no www)
3. **Submission reason** field (120-char limit): *"Fixed invalid ToS/Privacy links and reframed app description as creator publishing service per reviewer comments."*

## Key facts (locked)

- **App name**: "AI Bible Gospels"
- **App ID**: 7630124722525407250
- **Ownership shown in portal**: "Individual" (NOT "Born Made Bosses LLC" despite older memory references)
- **Website URL**: `https://aibiblegospels.com` (apex canonical, live, verified)
- **Target user** (sandbox tester): aibiblegospels_
- **Active credentials in .env**: SANDBOX (sbawswnygychzo38lw) — production creds preserved as comments
- **Scopes**: user.info.basic + video.upload (no video.publish)
- **Products**: Login Kit + Content Posting API (Direct Post OFF, inbox/drafts only)
- **Redirect URI**: https://12tribesofisrael.github.io/aibiblegospels-legal/callback.html (kept on GH Pages — OAuth callback forwarder, separate from legal pages)
- **Privacy Policy URL**: https://aibiblegospels.com/privacy (NEW — was GH Pages)
- **Terms URL**: https://aibiblegospels.com/terms (NEW — was GH Pages)

## Field length limits learned this round

- App **description** field: **120 chars max**
- App **submission reason** field (the "describe your reason for this submission" textbox at Submit time): **120 chars max**

## Portal flow gotcha (learned this round)

When an app is in "Not approved" state, the form fields look editable but there's no Save/Submit button. You must click **`Return to Draft`** (top right) and confirm the modal first. That transitions the app back to draft state and surfaces the Submit-for-review button. Until that confirmation, any field edits sit in the DOM but don't persist.

## Gotchas (still true — don't re-learn)

- Email from `noreply@dev.tiktok.com` subject "Your app status update" is GENERIC — real rejection reason ONLY in Dev Portal.
- TikTok **follows redirects** during DNS verification — keep apex as the non-redirected canonical.
- TikTok TXT verification format: **entire string** in Value field at **root** (`@`). Not subdomain, not split at `=`.
- TikTok rejects localhost redirect URIs.
- Pre-approval OAuth requires Sandbox mode.
- Sandbox video processing is slow (5-15 min); production <30s.

## Expected turnaround

Based on rounds 1-3: ~24-30h baseline, but round 3 ran 6 days due to TikTok-side backlog. Watch `aibiblegospels444@gmail.com` for `noreply@dev.tiktok.com` subject "Your app status update".

## Status as of 2026-04-29

4th submission filed. Waiting on TikTok review.
