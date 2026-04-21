---
name: When asked about a topic, read the memory file — not just MEMORY.md index
description: MEMORY.md index lines can drift from their underlying files; paraphrasing the index gave the user stale info and broke trust
type: feedback
originSessionId: 7836331d-eb91-4748-8dac-bbe96c586b92
---
When the user asks "what do you know about X" or asks for status on anything covered by an auto-memory file, read the underlying `<type>_<topic>.md` file with the Read tool. Do not paraphrase the one-line MEMORY.md index description.

**Why:** On 2026-04-21 the user asked about the TikTok app and I summarized from the MEMORY.md index line, which said "awaiting verdict after 1st rejection." The actual file `project_tiktok_app_review.md` had been updated hours earlier to reflect a 2nd rejection with three specific reviewer issues. My summary was stale, the user caught it, and trust took a hit — they explicitly asked "why did you miss it, and how do I know you're not missing other stuff?" The root cause was that MEMORY.md is pre-loaded into my context (easy to paraphrase from) while memory files require a tool call (one step of friction). That friction created the staleness.

**How to apply:**
- MEMORY.md is a table of contents. Treat it like one — use it to find the file, then read the file.
- If the user asks a status question (TikTok app, YPP appeal, Meta review, etc.), the Read tool call is cheap and the staleness risk is real.
- Exception: if the user asks "list what's in memory" or similar meta-questions, the index itself IS the answer.
- Separate lesson from the same session: MEMORY.md index lines and file bodies can drift silently — the session-end auto-sync on 2026-04-21 had updated the file body without updating the index line. Assume drift is possible; verify by reading.
