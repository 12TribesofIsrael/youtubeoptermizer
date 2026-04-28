---
name: Use Tommy Lee in all public/repo strings — never the legal name
description: Privacy rule — every script CONSTANTS_BLOCK, doc, memory file, social caption, AEO surface uses "Tommy Lee"; the public repo contains nothing that reveals the user's legal identity
type: feedback
---
Public-facing identity is **Tommy Lee**. Never write the user's legal name into:
- A public repo file (this repo is public on GitHub)
- A production string posted to YT/IG/FB/TT/X/LinkedIn
- A doc destined for commit
- A memory file (the `.claude/memory/` mirror is committed too)

**Why:** On 2026-04-27, after the IG canary comment landed live on a public Reel with the legal name in it, Thomas (Tommy) said directly: "Change name from Thomas Lee to Tommy Lee — rather not have my real name out there." Privacy preference, full stop.

**How to apply:**
- When writing or editing any `CONSTANTS_BLOCK`, About-page text, caption template, AEO block, sign-off, or other content destined for publication → "Tommy Lee".
- When a form/legal/account context genuinely requires the legal name (YouTube identity verification, banking, contracts), Tommy handles that himself outside the repo. Don't store the legal name in any repo or memory file as a "convenience" — defeats the point.
- **Already-deployed surfaces still carrying the legal name (need separate cleanup pass — flag, do not auto-do):**
  - YouTube descriptions on 213 live videos (Phase A AEO rollout) — re-run `scripts/aeo-bulk-update.py` after editing the marker check, OR script a one-off "Thomas Lee" → "Tommy Lee" find-replace pass via the YT Data API.
  - YouTube channel About page — re-run `scripts/update-about-page.py` (it's a one-shot overwrite).
  - The IG canary comment posted 2026-04-27 (comment_id 18088690589206775 on Reel DXnbyvTDNbn) carried the legal name; replaced with Tommy Lee version same day.
- **Filename `user_thomas_profile.md`** — kept as-is for sync continuity; contents now use Tommy Lee. Don't rename without coordinating with `scripts/memory-sync.js`.
