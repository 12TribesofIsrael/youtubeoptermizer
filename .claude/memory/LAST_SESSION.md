---
name: ""
metadata: 
  node_type: memory
  ended: 2026-05-27T00:00:00Z
  project: youtubeoptermizer
  branch: main
  originSessionId: 51b1b09d-2943-411c-a6ef-5b536434ea27
---

# Last Session — 2026-05-27

## What the user wanted
Build and validate the local FFmpeg assembler (replacing JSON2Video as last-mile video assembly), fix a subtitle timing bug discovered during validation, and document the tool for the BMB AI Automations repo.

## What we did
- Resumed mid-build from previous session; 19-scene validation render of 1 Maccabees Ch.3 had already completed (512 MB output)
- Discovered subtitle timing bug: karaoke captions raced ahead of audio because cumulative ASS offsets used raw MP3 durations, but each Pass A scene is ~2.4s longer than raw audio due to FFmpeg buffer overhead (not just 0.2s apad as assumed)
- Fixed by reordering phases in `scripts/assemble-video.py`: Pass A now runs before ASS writing; probed Pass A output durations drive cumulative subtitle offsets (commit e36f1b8)
- Fixed `\k` minimum floor to 2cs in `scripts/assemble/ass_writer.py` (Whisper 0-duration word glitch guard)
- Fixed Unicode arrow `→` → `->` in `scripts/assemble/ffmpeg_build.py` (Windows cp1252 crash)
- Verified fix with 3-scene canary — scene 2 events start at 0:00:14.63, exactly matching Pass A scene 1 duration
- Re-ran full 19-scene render (`output/renders/1maccabees-ch3.mp4`, 512.2 MB) — all intermediates cached, no API cost
- Updated `docs/local-ffmpeg-assembler.md` status from PLANNED to BUILT
- Wrote `C:\Users\Claude\bmb-ai-automations\docs\WALKTHROUGH-ffmpeg-video-assembler.md` (not committed — separate repo, separate Claude instance)
- Committed and pushed all youtubeoptermizer changes: e36f1b8

## Decisions worth remembering
- **Pass A duration ≠ raw audio + 0.2s**: actual overhead is ~2.4s per scene (FFmpeg 8.x behavior with `-stream_loop -1 -shortest -fflags +genpts`). Root cause unclear but probing Pass A outputs is the correct fix regardless of why.
- **All 19 fal.media Kling URLs still valid as of 2026-05-27** — clips cached locally.
- Integration is currently a two-step manual handoff: `render-via-pipeline.py --skip-json2video` writes manifest → user manually runs `assemble-video.py`. Tommy explicitly asked about automating this.

## Open threads / next session starts here
1. **Wire `--assemble` flag on `scripts/render-via-pipeline.py`**: ~10-line addition — after `--skip-json2video` writes the manifest path, automatically subprocess into `assemble-video.py`. Makes the full pipeline one command. Tommy asked about this; answer was "yes want me to wire that up?" and session ended before confirming.
2. **Commit the bmb-ai-automations doc**: `C:\Users\Claude\bmb-ai-automations\docs\WALKTHROUGH-ffmpeg-video-assembler.md` was written but not committed. Confirm with Tommy if that repo is open for direct commits.
3. **Tommy to review `output/renders/1maccabees-ch3.mp4`** — 3-scene canary confirmed timing fix works, but full 19-scene hasn't been visually reviewed yet. Check: Daniel voice all scenes, karaoke tracks speech end-to-end, no boundary pops.
4. **Modal deployment** — once full video review passes, ship assembler to Modal (container + FFmpeg + Whisper model in Volume + ElevenLabs key as Modal Secret + output to R2).
5. **Whisper upgrade**: consider making `small.en` the default model — better for KJV proper nouns (Maccabeus, Apollonius, etc.). Currently `base`.

## Uncommitted work
Clean working tree.
