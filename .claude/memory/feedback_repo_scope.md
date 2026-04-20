---
name: Repo scope rule for this session
description: From the youtubeoptermizer session only edit files in youtubeoptermizer; other repos are read-only. A separate Claude instance owns ai-bible-gospels
type: feedback
originSessionId: 3f97120f-9e3e-4e35-89e8-cf5aa8126068
---
From the youtubeoptermizer Claude session, stay inside `c:/Users/Claude/youtubeoptermizer/` for all writes. Other repos (notably `c:/Users/Claude/ai-bible-gospels/`) are **read-only** — allowed for research, grep, and reading files to inform work in this repo, but never for edits, config changes, commits, or deploys.

**Why:** A separate Claude instance owns the `ai-bible-gospels` Modal pipeline repo. Cross-repo edits from this session create drift and ownership confusion. User stated this rule explicitly on 2026-04-20 after I attempted to edit `ai-bible-gospels/workflows/custom-script/router.py` — the edit had to be reverted and the other instance then made the proper fix.

**How to apply:**
- Any Write / Edit tool call must target a path under `c:/Users/Claude/youtubeoptermizer/` OR the user's memory directory at `C:/Users/Deskt/.claude/projects/c--Users-Claude-youtubeoptermizer/memory/`.
- Read, Glob, Grep, WebFetch, WebSearch, and Bash read-only commands against other repos are fine — use them to research and inform recommendations.
- When the user asks for a pipeline fix, produce a recommendation (in chat or as a doc inside `youtubeoptermizer/drafts/` or `docs/`) and let them hand it to the other instance. Never propose pipeline edits from here as actionable steps I'll take.
- The only allowed git operations are `git` commands against the `youtubeoptermizer` repo. Do not `git commit` or `git push` inside `ai-bible-gospels/`.
