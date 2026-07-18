---
name: feedback_assembler_passa_stale_cache
description: assemble-video.py Pass A cache is existence-only — delete stale scene_*.mp4 before re-stitching or edits silently vanish
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 81f136bc-88c3-49b3-8591-4e4864024cc7
---

`scripts/assemble/ffmpeg_build.py` `pass_a()` caches each per-scene encode as
`output/scenes_tmp/<topic>/scene_<id>.mp4` and reuses it with a bare
`if out_path.exists()` check — it is NOT content-aware (unlike the TTS cache,
which uses a sidecar hash). So if you change a clip, a still→Ken-Burns rebuild,
an SFX file, or an sfx `volume` in the manifest and then re-run
`assemble-video.py --keep-intermediates`, Pass A **silently reuses the old
encode** and the final mp4 ships none of your changes.

**Why:** on 2026-07-17 the first re-stitch of the Eden doc reused the original
14:00 encodes and shipped ZERO of ~7 edits. Only caught it by comparing
`scene_*.mp4` mtimes against the changed source-clip mtimes.

**How to apply:** after changing ANY scene's clip/still/SFX/volume, delete that
scene's `output/scenes_tmp/<topic>/scene_<id>.mp4` (plus `concat_list.txt` and
`output/subs/<topic>/merged.ass`) BEFORE re-running the assembler. Then verify
by extracting a frame from the FINAL render at the scene's computed offset — do
not trust "done, exit 0". TTS stays cached (content-aware) so narration cost is
zero. Related: [[feedback_canary_before_bulk]], [[reference_eden_full_doc_pipeline]].
