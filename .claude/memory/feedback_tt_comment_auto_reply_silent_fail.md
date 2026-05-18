---
name: tt-comment-auto-reply-silent-fail
description: "Browser-automation TT comment replies have a silent-failure mode — type+Enter completes in DOM and editor clears, but TT bot-detection drops the comment server-side. Pre/post replyCount diff is mandatory."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 373f4945-6482-4d96-b023-f668cb24598b
---

Automated TT comment replies via Playwright (`page.type` into `.public-DraftEditor-content` + `page.keyboard.press('Enter')`) have a silent-failure mode: the action completes successfully in the DOM (chars typed, editor empties after Enter), but TT's bot-detection drops the comment server-side without raising any error.

**Why:** Tested 2026-05-16 with a 3-reply canary on the viral post (7629867741511486734). All 3 attempts reported "typed N chars" + "editor text after submit: EMPTY" — technically clean success signals. Verification by re-scraping showed @reginajohnson33's reply thread still had **0 replies** (confirmed NOT posted). Other 2 targets had pre-existing replies, so baseline unknown — also unverifiable.

Likely triggers: speed of click → type → submit, first-comment-in-session friction, Enter-key submit instead of explicit Post-button click, Draft.js text without IME/composition events.

**How to apply:**
- **Don't trust "editor empty after submit" as success.** It only proves the editor was cleared (which Draft.js does on submit-attempt regardless of server outcome).
- **Verification = pre-action `View N replies` count vs post-action count, on the SAME target.** Anything else is guessing.
- For batch reply work, prefer:
  - **Manual** — paste from `output/tt-comments-to-reply.md` queue (the [[reference_tt_comment_scraper_workflow]] output)
  - **Semi-supervised** — Claude opens browser, scrolls to commenter, clicks Reply, pre-fills text. User presses Enter manually. Zero ban risk because every send is a real keystroke.
- The TT Content Posting API does NOT include comment-management scope (see [[project_tiktok_app_review]]) — no clean API path exists.
- Account-level risk: at 1,055 followers riding a viral wave, repeated bot-pattern detection could shadow-ban. Not worth saving 15 min over.
