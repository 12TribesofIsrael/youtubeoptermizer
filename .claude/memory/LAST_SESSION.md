---
ended: 2026-04-27T00:00:00Z
project: youtubeoptermizer (AI Bible Gospels)
branch: main
originSessionId: this-session
---
# Last Session — 2026-04-27

## What the user wanted
"Check on the status of our apps." App-review status check across Meta IG, TikTok, and YPP — saved-memory snapshots were 2-4 days old and the deadlines they cited had all passed, so this session existed to get a current, verified read.

## What we did
- Tried Gmail (the authoritative source). [token_aibiblegospels444.json](C:/Users/Owner/.claude/skills/gmail-inbox/token_aibiblegospels444.json) refresh fails with `invalid_scope`: token saved with `[gmail.modify, labels, settings.basic, spreadsheets, drive]` but [gmail_unified.py:39-43](C:/Users/Owner/.claude/skills/gmail-inbox/scripts/gmail_unified.py#L39-L43) requests `[gmail.modify, labels, send]`. Send scope missing → Google rejects refresh. **Did not re-auth** (would need browser flow).
- Built [scripts/meta-priv-probe.py](scripts/meta-priv-probe.py) — probes all 5 advanced IG Business scopes via `graph.instagram.com/v23.0`. Result: **all 5 PASS** (basic, manage_comments, manage_insights returned reach 93/56, manage_messages, content_publish container created).
- End-to-end caption write also confirmed: POST to `/{media_id}` with `caption` + `comment_enabled=true` → `{"success":true}` HTTP 200. **Meta App Review is APPROVED & LIVE.** First write was on the most-recent post `18100711882824083` (Minister Zay tracker, posted ~2h before probe) — flagged the side effect to user (caption round-tripped, comments re-asserted on).
- TikTok: `client_credentials` grant against prod key `awhtm3emzgjcvin6` returned 200 + token, but per [feedback_tiktok_approval_probes.md](C:/Users/Owner/.claude/projects/c--Users-Owner-repos-youtubeoptermizer/memory/feedback_tiktok_approval_probes.md) that's a known false positive. User then shared dev-portal screenshot: **"In review"** on Production tab, with portal banner attributing the slow turnaround to a TikTok-side backlog. Day 5, no rejection — just queued.
- Synced memory: rewrote [project_meta_app_review_status.md](C:/Users/Owner/.claude/projects/c--Users-Owner-repos-youtubeoptermizer/memory/project_meta_app_review_status.md) to "APPROVED & LIVE 2026-04-27" with the verified scope-probe evidence; appended day-5 "In review" status + "do not click Recall" warning to [project_tiktok_app_review.md](C:/Users/Owner/.claude/projects/c--Users-Owner-repos-youtubeoptermizer/memory/project_tiktok_app_review.md); updated MEMORY.md index lines for both.
- Committed and pushed: [c89f406](https://github.com/12TribesofIsrael/youtubeoptermizer/commit/c89f406) (`Add Meta IG Business privileged-scope probe`).

## Decisions worth remembering
- **Caption updates require `comment_enabled` param** on graph.instagram.com — without it, IG returns IGApiException code 100. Worth checking whether [scripts/meta-update-posts.py](scripts/meta-update-posts.py) already passes this before the bulk 538-post run, or a 538-post failure cascade is on the table.
- Did NOT re-auth Gmail this session. The fix is one of: (a) update [gmail_unified.py:39-43](C:/Users/Owner/.claude/skills/gmail-inbox/scripts/gmail_unified.py#L39-L43) `SCOPES` to match the actual token (drop `gmail.send`, add the rest), or (b) re-run the OAuth flow with the script's current scopes. Probably (a) is right since Thomas doesn't seem to use `gmail.send` from this script.

## Open threads / next session starts here
- **Bag the Meta win.** Run `python scripts/meta-update-posts.py instagram --live` for the 538 IG captions. Verify the script passes `comment_enabled` before the bulk run — if not, the round-trip will fail with the IGApiException code 100 we saw. Suggest a dry-run on 1-3 posts first.
- **Gmail auth is broken.** Fix [gmail_unified.py:39-43](C:/Users/Owner/.claude/skills/gmail-inbox/scripts/gmail_unified.py#L39-L43) `SCOPES` so refresh works without re-OAuth (or re-OAuth if `gmail.send` is actually wanted). Currently blocking any Gmail-driven verification of TikTok approval emails.
- **TikTok**: just wait. Don't click `Recall` in the dev portal — that withdraws and forces a 4th submit. Re-check dashboard or Gmail (once unblocked) in 1-2 days.
- **YPP**: 72 days to 2026-07-08 reapply. Phase 4B long-form is still the highest-leverage runway — trailer script written, 4-6 animated explainers (10-20 min) unstarted. AEO Phase B (per-video LLM content) is the secondary track, paced over the same window.

## Uncommitted work
Clean working tree. 0 commits ahead of origin/main.

## Focus note
session-end
