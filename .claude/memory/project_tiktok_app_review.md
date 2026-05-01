---
name: TikTok App Review status
description: 4th rejection 2026-05-01 fixed with multi-tenant pivot; /connect/tiktok OAuth flow built and verified live on aibiblegospels.com; 5th submit pending demo re-record
type: project
originSessionId: 3f97120f-9e3e-4e35-89e8-cf5aa8126068
---
TikTok Content Posting API app review — **4th rejection 2026-05-01** addressed structurally via multi-tenant OAuth flow on aibiblegospels.com. **5th submission pending** demo re-record + production config updates.

## Timeline

- **2026-04-18** — 1st submission as "Ai-Bible-Gospels"
- **2026-04-20 02:18 UTC** — 1st rejection: name mismatch (app "Ai-Bible-Gospels" vs website/legal "AI Bible Gospels")
- **2026-04-20** — renamed app to "AI Bible Gospels" (spaces), resubmitted
- **2026-04-21 08:57 UTC** — 2nd rejection: Website URL + Demo video
- **2026-04-22** — 3rd submission after full fix pass (see below)

## 2nd rejection reasons (verbatim, 2026-04-21)

- **Website URL** — "cannot be a landing page or login page. You must have an externally facing fully developed website."
- **Demo video** — "must show the complete end-to-end flow... all selected products and scopes must be clearly demonstrated... required to use sandbox."

## Apr 22 fix pass (what changed before 3rd submit)

1. **Website URL** → `https://aibiblegospels.com` (live Next.js/Vercel site, verified via TikTok DNS TXT after flipping apex as primary). Replaced the legal-pages GH URL.
2. **Apex as primary in Vercel** — previously `aibiblegospels.com` 308'd to `www.aibiblegospels.com`; reversed so apex serves directly, www→apex. Fixed DNS TXT verification failure (www is CNAME to Vercel, blocks TXT per spec).
3. **DNS TXT at root** — `tiktok-developers-site-verification=KwMOkEST8r3pyyR2bg2YFuveU8x88zEX` at `@` in GoDaddy. Prior attempt split the string wrong (put prefix as Name, token as Value at subdomain) — TikTok's actual format is full string in Value at root.
4. **Privacy + Terms footer links** on aibiblegospels.com (pointing to existing legal URLs on GH Pages). Added via aibiblegospelscom repo (separate Claude instance).
5. **Re-recorded sandbox demo** showing: site tour → OAuth consent (both scopes visible) → user info call → video upload → inbox confirmation.
6. **Scope explanation** rewritten to be specific (prior was 7 words for video.upload — reviewer flagged as vague).

## Key facts (locked)

- **App name**: "AI Bible Gospels" (Organization: Born Made Bosses LLC)
- **Website URL**: `https://aibiblegospels.com` (apex canonical, live, verified)
- **Target user** (sandbox tester): aibiblegospels_
- **Active credentials in .env**: SANDBOX (sbawswnygychzo38lw) — production creds preserved as comments
- **Scopes**: user.info.basic + video.upload (no video.publish)
- **Products**: Login Kit + Content Posting API (Direct Post OFF, inbox/drafts only)
- **Redirect URI**: https://12tribesofisrael.github.io/aibiblegospels-legal/callback.html
- **Privacy Policy URL**: https://12tribesofisrael.github.io/aibiblegospels-legal/privacy.html
- **Terms URL**: https://12tribesofisrael.github.io/aibiblegospels-legal/terms.html

## Gotchas (still true — don't re-learn)

- Email from `noreply@dev.tiktok.com` subject "Your app status update" is GENERIC — real rejection reason ONLY visible in Dev Portal, not email body.
- TikTok **follows redirects** during DNS verification. If Website URL is apex but apex redirects to www, TikTok looks for TXT at www — which may be a CNAME (blocks TXT). Fix: make apex the non-redirected canonical.
- TikTok TXT verification format: **entire string** (`tiktok-developers-site-verification=<token>`) goes in the **Value** field at **root** (`@`). NOT subdomain, NOT split at the `=`.
- TikTok rejects localhost redirect URIs. Use GH Pages forwarder (`callback.html`).
- Pre-approval OAuth requires Sandbox mode — production creds return `client_key` error until approved.
- Dev Portal won't save app config without a placeholder demo video first. Upload any mp4, save, swap real demo later.
- Sandbox video processing is slow (5-15 min for PROCESSING_UPLOAD → SEND_TO_USER_INBOX); production <30s.

## Expected turnaround

Based on prior 2 rounds: ~24-30 hours. Watch `aibiblegospels444@gmail.com` for `noreply@dev.tiktok.com` email subject "Your app status update".

## Status as of 2026-04-27 (day 5)

Dev portal screenshot confirms **Production tab → "In review"**. TikTok banner: *"This version of AI Bible Gospels is in review. There may be a delay in the app review process due to a high volume of requests."*

Round 3 is running long vs the 24-30h baseline — TikTok-side backlog, NOT a problem with the submission.

## 4th rejection (2026-05-01) — STRUCTURAL, not a config problem

Reviewer notes (verbatim, on Website URL field):
- "App will not be approved for personal or company internal use."
- "Your website does not have a login entry point. How can users complete the login process and use the Content Posting API service on your website?"
- "TikTok for Developers currently does not support personal or internal company use. Not acceptable: Display posts from the TikTok account(s) you or your team manage on your website."

**Root cause:** TikTok categorizes the entire submission as "internal/personal use" — the app, demo, and website all read as a tool to manage AI Bible Gospels' own TikTok. The Content Posting API is **only** approved for multi-tenant services where third-party TikTok users authenticate and the app posts on their behalf. No amount of copy editing fixes this.

**Three paths forward:**
1. **Multi-tenant pivot** — build a real "Login with TikTok" entry point + minimal client portal on aibiblegospels.com, reframe submission as a faith-tech scheduling tool for ministers/streamers (aligns with 2026-04-29 brand positioning), re-record demo with an external user. Requires changes in aibiblegospelscom repo (READ-ONLY from this project — handoff to other Claude instance).
2. **Walk away** — manual posting works; abandon the API review, save the time, reapply later only if real client demand emerges.
3. **Light pivot** — add an OAuth landing page only, no portal. Likely fails the "how do users use the service" question.

**Recommendation:** path 2 (walk away) unless there's actual client demand for "schedule TikTok via our tool" — TikTok review will keep failing until the product is genuinely multi-tenant, and that's real product work, not paperwork.

## 2026-05-01 multi-tenant build (path 1 chosen + executed)

Tommy chose path 1. Built and pushed to `aibiblegospelscom` repo (`9f454a3 Add TikTok OAuth login flow at /connect/tiktok`):

- **`/connect/tiktok`** — public marketing page with "Connect with TikTok" button
- **`/api/tiktok/start`** — generates CSRF state cookie, redirects to TikTok OAuth
- **`/api/tiktok/callback`** — validates state, exchanges code, fetches user info, redirects to success
- **`/connect/tiktok/success`** — confirmation page with activation CTA (email aibiblegospels444@gmail.com)
- **`/connect/tiktok/error`** — handles `access_denied` / `state_mismatch` / `token_exchange_failed`
- Homepage gains a "For creators" section (between YouTube and Work-with-us) + footer Connect link
- Sitemap includes `/connect/tiktok`
- Privacy/Terms already had multi-tenant framing — no changes needed

**Vercel env vars** set on production (sandbox creds for now): `TIKTOK_CLIENT_KEY=sbawswnygychzo38lw`, `TIKTOK_CLIENT_SECRET` (from `youtubeoptermizer/.env`).

**TikTok dev portal** updated: added `https://aibiblegospels.com/api/tiktok/callback` to **sandbox** Login Kit redirect URIs (the production redirect URI list is separate; both registered).

**Verified end-to-end live** — Tommy completed full round-trip: aibiblegospels.com → /connect/tiktok → click Connect → TikTok consent → approved → redirected to /connect/tiktok/success.

## Open items before clicking Submit for review (5th attempt)

1. **Production app description** must NOT say "our own TikTok account" or any "internal/personal use" phrasing — that triggered rejection #4. Rewrite to multi-tenant: e.g. "Lets ministers, Christian streamers, and missions teams schedule and publish faith content to their own TikTok accounts."
2. **Demo video re-record** — use the new flow (homepage → /connect/tiktok → external sandbox tester consents → success page). Old demo showed Tommy's own account = "internal use" trigger.
3. **Per-scope explanations** — `user.info.basic`: "confirms which creator's account is connected." `video.upload`: "uploads creator-submitted content to the creator's own TikTok inbox as drafts for their review and publication."
4. **Submission reason** (120-char field): suggested — "Multi-tenant content publisher for ministers and Christian creators. Login at aibiblegospels.com/connect/tiktok."

## Sandbox upload demo (in flight as of 2026-05-01 13:42 UTC)

Test upload `v_inbox_file~v2.7634916387802351630` (64 MB / 71s vertical 9:16 / `short_1_00_51_to_02_02.mp4`) chunked + uploaded successfully. Status stuck at `PROCESSING_UPLOAD` past 15-min poll cap. Sandbox queue is slow today; will eventually flip to `SEND_TO_USER_INBOX`. Manual re-check: `python scripts/tiktok-status.py "v_inbox_file~v2.7634916387802351630"`.

## Bug fixed: `scripts/tiktok-post.py` chunk math

Original computed `total_chunks = ceil(video_size / chunk_size)` — produces a last chunk that can be smaller than `chunk_size`, which TikTok rejects with `invalid_params: The total chunk count is invalid`. Fix: for files ≤64 MB use single-chunk upload; for larger files use `total_chunks = video_size // chunk_size` so last chunk absorbs remainder (size lands in `[chunk_size, 2 × chunk_size)` per TikTok's rule).
