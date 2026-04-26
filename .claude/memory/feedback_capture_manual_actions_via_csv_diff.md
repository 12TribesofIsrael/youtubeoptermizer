---
name: Capture user's manual catalog actions retroactively via CSV diff
description: When the channel state diverges from what was logged (video count mismatch, missing entries), don't ask the user to recall — diff the latest analytics CSV against the prior committed snapshot from git history.
type: feedback
originSessionId: 99dd36aa-4c34-41a4-bbcb-873e1777ecc2
---
When you notice the channel video count or playlist contents diverge from what the prior session log said (e.g. session-log expected 207 videos, fresh export shows 187), don't ask Thomas to recall what he deleted. Reconstruct it via CSV diff.

**Why:** Thomas works between Claude sessions in YouTube Studio directly. He follows consistent rules ("removed all Shorts under 500 views") but doesn't pause to log each batch. The data is recoverable from git because we commit `analytics/post-optimization/Table data.csv` after every export — every commit holds a full snapshot of the catalog at that point, with title + duration + view-count metadata.

**How to apply:**
1. `git log --oneline "analytics/post-optimization/Table data.csv"` — find the most recent commit before the unaccounted change.
2. `git show <sha>:"analytics/post-optimization/Table data.csv" > prev_table_tmp.csv` (use a local repo path, NOT `/tmp/...` — `/tmp` doesn't survive across Bash tool turns on Windows).
3. Build a Python diff: `set(prev) - set(current)` for video IDs, then categorize by his stated rule (duration band + view threshold).
4. Filter out anything already documented (the kill-list, prior changelog entries) so the new entry only captures what's truly missing.
5. Add a changelog entry crediting Thomas for the action with the rule he used, and list IDs grouped by category. Title it like "Manual cleanup captured retroactively" so the provenance is obvious.

**Important:** chain `git show > file.csv` and the Python that reads the file in a SINGLE Bash invocation (or use a local path that persists). They can't be split across two Bash tool calls — the temp file gets wiped between calls.
