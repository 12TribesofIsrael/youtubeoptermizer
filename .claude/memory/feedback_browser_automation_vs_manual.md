---
name: Don't parallel-drive a portal Thomas is already in
description: When Thomas has a portal/admin UI open in his own browser, don't try to automate the same flow via Playwright — give copy-paste values and let him drive
type: feedback
originSessionId: 902a63d9-43f4-44f8-947d-455372616484
---
When Thomas is actively in a portal/admin UI in his own Chrome session, do **not** try to drive the same flow via the Playwright browser skill in parallel.

**Why:** The two browser instances run separate state. On 2026-04-29 during the TikTok 4th-submission fix, Thomas clicked "Return to Draft" in his Chrome but the Playwright session (different browser instance, shared persistent profile but separate page state) still showed the old "Not approved" state. We wasted ~3 cycles probing the desync. Eventually I clicked Return-to-Draft via Playwright too, which opened a confirm modal — but the browser pilot's `wait_for_user` timed out and closed before he could click Confirm. He pushed back: *"I seen it you closed it to fast let me click it"* and then *"just tell me what to put everywhere and I'll do it if you can't"*.

**How to apply:** When the user is actively in a portal:
- Default to giving copy-paste values they can use directly. They are faster than Playwright and already authenticated.
- If automation would genuinely save them time (e.g. 10+ fields, repetitive data entry), say so explicitly and ask before launching Playwright.
- If you do launch Playwright and a confirmation modal appears, do NOT use `wait_for_user` for it — Playwright's brief keep-open windows aren't enough. Instead: tell them what the modal says, ask them to handle it in their own session, and pick up from the resulting state.
- Investigation/screenshot use of Playwright is fine — it's reading state, not driving multi-step flows the user can do faster manually.
