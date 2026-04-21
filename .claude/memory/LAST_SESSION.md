---
ended: 2026-04-21T23:30:00Z
project: youtubeoptermizer (AI Bible Gospels)
branch: main
originSessionId: d6d44c50-a641-4f85-b422-6b0200ea977c
---
# Last Session — 2026-04-21

## What the user wanted
Status check on the three in-flight platform reviews: Meta App Review, TikTok App Review, and the YouTube YPP suspension appeal. Wanted clear answers on what's approved, pending, or rejected.

> Note: a separate Claude instance ran a parallel session on a different machine earlier today (viral-formula Clone #2 flop diagnosis + locking hook rules). That work pushed to origin between my session-end attempts. Its findings are preserved in durable memory files (`reference_tiktok_scraping_selectors.md`, `feedback_save_skill_learnings.md`, `project_tiktok_app_review.md`, updated `docs/viral-formula-deuteronomy-28.md`). Not re-summarizing here — see those files + its commits `1e660e7`, `371963d`, `2f0daa8`, `7dd6c06` for detail.

## What we did (this machine)
- Probed Meta access token via `debug_token` — token is **INVALID** (recurring expiry issue) and still carries old `graph.facebook.com` IG scopes, not the new `instagram_business_*` perms submitted 2026-04-17. Cannot infer approval status until token is refreshed. Review window: day 4 of 10, expect decision ~2026-04-28.
- Probed TikTok `/v2/user/info/` — 401 `access_token_invalid`; TikTok token expired 2026-04-19. Still on SANDBOX creds (`sbawswnygychzo38lw`).
- User shared screenshot: **TikTok App Review rejected AGAIN 2026-04-21** (2nd rejection). Reviewer cited (1) Website URL cannot be login/landing page — needs real externally-facing site, (2) demo video unclear + must show all scopes end-to-end in sandbox, (3) trim unused products/scopes. Merged this with the 2026-04-20 name-mismatch rejection (from the other machine's earlier commit) into a unified 2-rejection timeline in `project_tiktok_app_review.md`.
- Recapped YPP suspension state from memory: appeal submitted 2026-04-10, 14-day window closes ~2026-04-24 (3 days away), hard deadline 2026-04-30. Do-not-touch rule on videos/titles/thumbnails remains in force; keep 1 Maccabees uploads flowing.
- Hit a merge conflict on `.claude/memory/project_tiktok_app_review.md` during auto-sync (remote had the 2026-04-20 1st-rejection write, local had the 2026-04-21 2nd-rejection write). Resolved by reconstructing full timeline rather than picking a winner. Pushed as `f607a47` → `cfe30c3`.

## Decisions worth remembering
- When merging divergent memory edits from two machines, reconstruct a single timeline rather than pick one winner — both historical events matter.
- Did not open dev dashboards via Playwright — user supplied the TikTok rejection screenshot directly. Meta dashboard check deferred until after 2026-04-24 (first natural checkpoint for both Meta decision and YPP decision).

## Open threads / next session starts here
- **TikTok resubmit #3** — three blockers: (1) stand up a real content/marketing website separate from `aibiblegospels-legal` GH Pages repo (About/What we do/Contact), (2) re-record sandbox demo narrating each scope end-to-end, (3) trim products/scopes to exactly what's demoed. User was offered scaffolding help but didn't answer; resume by asking.
- **Meta App Review** — refresh the expired `META_ACCESS_TOKEN` (recurring blocker), re-run `scripts/meta-app-review.py` debug_token to verify new `instagram_business_*` scopes are granted. Decision expected ~2026-04-28.
- **YPP decision** — ~2026-04-24 (3 days). Until then: no video/metadata/thumbnail edits. Keep 1 Maccabees uploads flowing.
- **Script 3 (Smallest Nation)** — open from the other machine's session. Hook now compliant ("They don't teach this in church. Read Deuteronomy 7 slowly. ☦️") per locked rules in `docs/viral-formula-deuteronomy-28.md`. Before posting: duration ≤55s, Daniel voice, 9:16, face-forward Scene 1 thumbnail.
- **Clone #1 + #2 TikTok cleanup decision** — still open. ⚠ YPP rule says "do NOT delete videos until appeal resolves" — that's YouTube-specific but flag before any TikTok delete.
- **Seed video cooling** — 2,700 → 3,999 views in ~48h, won't hit 20K–100K projection. Decision needed: ship fresh compliant clone to reactivate, or accept cool-down.
- **Skills repo copy (paused)** — user started a snippet to copy session-end/session-start skills to a local claude-skills repo. Repo path never provided. Resume by asking.

## Uncommitted work
Clean working tree. Local = origin at `7dd6c06`.
