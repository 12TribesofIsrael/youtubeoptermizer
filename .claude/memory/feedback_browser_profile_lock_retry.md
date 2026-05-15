---
name: browser-skill-profile-lock-retry-pattern
description: "browser_pilot.py exit code 21 = profile lock from prior run's Chrome not fully released. Sleep 5 + retry works. Don't nuke the profile."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f3a977cd-ea4f-4269-862c-b8e70bf59422
---

When `~/.claude/skills/browser/scripts/browser_pilot.py` fails immediately with `TargetClosedError` and the launched chrome process exits with code **21**, that's a profile lock from a previous run whose Chrome instance hasn't fully released `~/.meta-playwright-profile/`.

**Fix:** `sleep 5 && python ~/.claude/skills/browser/scripts/browser_pilot.py <actions.json>` — retry works. Confirmed working 2026-05-13 on the TikTok dashboard scrape.

**Why:** Chrome takes a few seconds to release the SingletonLock equivalent after a context.close(). Back-to-back browser_pilot invocations within the same conversation can hit this. Reboot is NOT required — just wait.

**How to apply:**
- Exit code 21 → retry once with a 5-sec sleep, don't escalate.
- Don't ask the user to reboot or to log out — that's overkill.
- Don't touch the persistent profile directory — it holds 15+ service logins from the sweep.

**Distinguish from a different failure mode:** exit code `2147483651` (STATUS_BREAKPOINT, 0x80000003) is genuine profile corruption — Chromium starts, touches profile files, then crashes. That one is NOT solved by retry/reboot; it needs targeted file repair (Cookies SQLite or Network state) or a profile rebuild. Hit this earlier in the same 2026-05-13 session; was resolved by whatever update Thomas ran outside the conversation. Don't conflate the two exit codes.
