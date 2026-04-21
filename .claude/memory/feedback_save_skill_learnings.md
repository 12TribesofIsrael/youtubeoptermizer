---
name: Save skill gotchas into the skill's own file
description: When you discover a gotcha about how a skill works, edit the skill's SKILL.md to document it so future sessions don't re-discover it
type: feedback
originSessionId: 5618946d-736d-4ccd-ab23-199943513a3f
---
When I find out something non-obvious about how a skill behaves (bug, wrapping behavior, argument quirk, required pattern), save that knowledge to the skill's own `SKILL.md` rather than just fixing it in-session. Project-specific selectors or patterns go into a project auto-memory `reference_*.md` instead.

**Why:** The user explicitly asked on 2026-04-21 after I burned three iterations rediscovering that the browser skill's `evaluate` action wraps scripts in `() => { <script> }` (so IIFEs return null and you must use `return`). They want that pain paid once, not every session. Skills are shared across projects and machines — editing `~/.claude/skills/<skill>/SKILL.md` makes the lesson persistent for everyone who uses the skill.

**How to apply:**
- Global gotchas about a skill's wrapping/API/syntax → edit the skill's SKILL.md (e.g. `~/.claude/skills/browser/SKILL.md`). Add a "Gotchas" or "Critical notes" section with concrete before/after examples.
- Project-specific selectors, API quirks, or patterns → write a `reference_*.md` in the project auto-memory and add a pointer line to `MEMORY.md`.
- Don't bury the lesson in a session log — it gets lost. Durable memory/skill file is the right home.
- Example from 2026-04-21: added 5-point "`evaluate` action — critical gotchas" section to `~/.claude/skills/browser/SKILL.md` covering the wrapping, `return` requirement, escape rules, truncation, and a debug pattern.
