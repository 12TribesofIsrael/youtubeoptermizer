---
name: reference-post-production-pipeline
description: Where the intro+outro+logo post-production pipeline lives in this repo and how it works
metadata: 
  node_type: memory
  type: reference
  originSessionId: 15371fc8-3343-4eb2-86d4-f785dc9e9b70
---

The branded post-production pipeline (adds intro, outro, and logo to a
finished/ready video) now lives IN this repo: `scripts/post_produce.py`.
Ported 2026-07-17 from ai-bible-gospels `workflows/biblical-cinematic/scripts/
post_produce.py` (the source of truth; that repo's `batch_post_produce.py` and
`assets/README.txt` there are STALE/broken — ignore them).

How it works:
- Drop a ready video in `postproduction/`, run `python scripts/post_produce.py`
  (auto-picks newest), output lands at `output/<name>_final.mp4`.
- Assets in `assets/postproduction/`: `intro_outro.mp4` (ONE merged brand clip,
  ~155.6s) + `logo1.png`. Both gitignored (*.mp4/*.png) since repo is public —
  they live locally only; re-copy from ai-bible-gospels to refresh.
- The single merged brand clip is split at `DEFAULT_SPLIT`: intro = brand[0..split],
  then your main video (logo overlaid bottom-left, main ONLY), then outro =
  brand[split..end]. Concats via ffmpeg after normalizing all 3 segments.
- `DEFAULT_SPLIT = 27.6` (NOT 26). 26 sliced the "Story of Israel's Return"
  identity card mid-frame (card runs ~19.6-27.567s), replaying its tail at the
  top of the outro. 27.6 keeps the cut on the scene boundary. Don't lower it.
- Flags: `--split`, `--width` (default = match source; 1920/3840 to force),
  `--no-logo`. Needs ffmpeg+ffprobe on PATH.
- Known todo: the outro's THANK YOU/SUBSCRIBE card holds ~113s (long tail); no
  outro-trim flag yet — add an outro-end cap if the user wants it shorter.

Related: the `add-covers` skill wraps the same logic. See [[reference-remotion-doc-framework]]
for the separate Remotion (not ffmpeg) branded-video path.
