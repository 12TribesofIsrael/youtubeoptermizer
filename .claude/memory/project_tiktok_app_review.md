---
name: TikTok App Review status
description: APPROVED 2026-05-06 on 5th submission; Content Posting API live with user.info.basic + video.upload (inbox/drafts only)
type: project
originSessionId: 3f97120f-9e3e-4e35-89e8-cf5aa8126068
---
TikTok Content Posting API app review — **APPROVED 2026-05-06** on the 5th submission.

## Final state

- **App name**: "AI Bible Gospels" (Organization: Born Made Bosses LLC)
- **Status**: Production / live
- **Products**: Login Kit + Content Posting API (Direct Post OFF, inbox/drafts only)
- **Scopes granted**: `user.info.basic` + `video.upload`
- **Scope NOT granted**: `video.publish` (direct-to-feed) — would require separate approval; not requested
- **Production client_key**: `awhtm3emzgjcvin6` (now active in `.env`)
- **Sandbox client_key**: `sbawswnygychzo38lw` (kept for dev testing — separate dev portal config)
- **Website URL**: `https://aibiblegospels.com` (apex canonical)
- **Terms URL**: `https://aibiblegospels.com/terms` (Next.js route on aibiblegospelscom repo)
- **Privacy URL**: `https://aibiblegospels.com/privacy` (Next.js route on aibiblegospelscom repo)
- **Redirect URI (script)**: `https://12tribesofisrael.github.io/aibiblegospels-legal/callback.html`

## Submission timeline (for the record)

| # | Date | Outcome | Reason |
|---|---|---|---|
| 1 | 2026-04-18 | Rejected 2026-04-20 | Name mismatch (`Ai-Bible-Gospels` vs `AI Bible Gospels`) |
| 2 | 2026-04-20 | Rejected 2026-04-21 | Website URL was login page; demo video incomplete |
| 3 | 2026-04-22 | Rejected 2026-04-28 | Invalid ToS/Privacy links; "internal use" framing |
| 4 | 2026-04-29 | Rejected 2026-05-01 | (covered by [tiktok-app-review-2026-04-29.md](../../../youtubeoptermizer/docs/tiktok-app-review-2026-04-29.md)) |
| 5 | 2026-05-01 | **APPROVED 2026-05-06** | Multi-tenant OAuth + chunk-math fix |

## What's unblocked now

1. End-to-end posting: Shorts → TikTok drafts via `python scripts/tiktok-post.py --video path.mp4`
2. Multi-tenant OAuth via `aibiblegospels.com` (already built — separate Claude instance owns that repo)
3. `creator_info` queries return real privacy/mode capabilities

## What's still gated

- `video.publish` scope (direct-to-feed posting) — would need separate approval round
- Mass-DM-to-followers — TikTok API doesn't expose this even after approval (see `project_tiktok_hook_formula.md` and 2026-05-02 session log)

## Action item after approval

Sandbox-issued access tokens do NOT work against the production `client_key`. After swapping `.env` to prod creds, must re-OAuth once: `python scripts/tiktok-post.py --auth-only`.

## Gotchas (still true post-approval)

- Email from `noreply@dev.tiktok.com` subject "Your app status update" is GENERIC — real status only in Dev Portal.
- Sandbox config and Production config are separate spaces in the dev portal — saving in one does not propagate (see `feedback_tiktok_sandbox_separate_config.md`).
- TikTok rejects localhost redirect URIs — use the GH Pages forwarder.
- Sandbox video processing is slow (5-15 min); production should be <30s.
