---
name: feedback_ffmpeg_pass_a_duration_overshoot
description: "FFmpeg Pass A output is ~2.4s longer than raw audio per scene — not just apad's 0.2s — causing subtitle drift; always probe Pass A outputs for ASS offsets"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 51b1b09d-2943-411c-a6ef-5b536434ea27
---

Each FFmpeg Pass A output (looped Kling clip + narration audio + apad) is approximately 2.4s longer than the raw narration MP3, NOT just 0.2s from `apad=pad_dur=0.2`.

**Why:** Confirmed on FFmpeg 8.1.1 with `-stream_loop -1 -shortest -fflags +genpts`. Root cause unclear (likely interaction between `-shortest` and `-stream_loop` with PTS generation in FFmpeg 8.x). Kling clips are ~15s each; raw narrations ~12-32s; Pass A outputs are raw + ~2.4s consistently.

**How to apply:** Never use raw MP3 durations to calculate cumulative subtitle offsets for a multi-scene merged ASS file. Always probe the Pass A MP4 outputs. In `assemble-video.py`, Pass A runs BEFORE subtitle writing, then `probe(scene_paths[sid])["duration_s"]` drives `write_merged_ass()`. Without this, by scene 14 the subtitles are `13 × 2.4 = 31s` ahead of audio — looks like karaoke is "going super fast."

Fix committed at e36f1b8 in youtubeoptermizer.
