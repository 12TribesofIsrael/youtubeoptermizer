---
name: Scrub personal info before committing to public repo
description: youtubeoptermizer repo is public on GitHub; remove emails/personal details from docs before commit
type: feedback
originSessionId: e01c4309-a261-40e2-8977-ae82d2e592ab
---
The `12TribesofIsrael/youtubeoptermizer` repo is **public on GitHub**. Before committing any doc/script/strategy file that may contain personal contact info (email addresses, phone numbers, home/billing addresses, account IDs that could enable phishing), scrub those values and replace with bracket placeholders like `[channel owner email]`.

**Why:** On 2026-04-22 a YPP appeal draft ([docs/ypp-appeal-2026-04.md](docs/ypp-appeal-2026-04.md)) had `aibiblegospels444@gmail.com` written into it for the user's reference. Committing it would have exposed that address to scrapers/spammers via the public git history indefinitely (git history can't be cleanly purged without a force-push rewrite). Caught and scrubbed before commit `7db9733`.

**How to apply:**
- For in-repo docs destined for commit: scrub personal emails, phone numbers, physical addresses, exact dollar amounts from personal accounts.
- Internal references to the channel handle (@AIBIBLEGOSPELS), the channel's brand-identity rules, competitor analysis, public analytics numbers — all fine to commit; those are public-domain.
- Keep the un-scrubbed version in the auto-memory directory (`C:\Users\Owner\.claude\projects\...\memory\`) if future sessions need it — that directory is NOT synced to the public repo by default (the central backup repo, if any, is separately managed).
- When in doubt on a borderline file, ask before committing rather than defaulting to include.
