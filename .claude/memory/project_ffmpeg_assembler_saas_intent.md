---
name: project_ffmpeg_assembler_saas_intent
description: "FFmpeg assembler is intended as a hosted SaaS product on aibiblegospels.com, not just a local tool — architecture must support multi-tenant hosted rendering"
metadata: 
  node_type: memory
  type: project
  originSessionId: 51b1b09d-2943-411c-a6ef-5b536434ea27
---

The local FFmpeg assembler (scripts/assemble-video.py) is a stepping stone to a hosted SaaS product under the aibiblegospels.com faith-tech tools brand ("Software in service of the calling"). Ministry leaders/streamers upload a script → get back a branded MP4 with Daniel-style narration + karaoke subs.

**Why:** aibiblegospels.com is positioned as faith-tech for ministers/streamers/missions. The assembler is the core rendering capability that becomes a hosted product.

**How to apply:** When building or extending the assembler, architecture decisions must account for:
- Multi-tenant input (manifest JSON per job, not local files)
- Output stored in cloud storage (R2 or S3), not local disk
- Compute runs on Modal (already in Tommy's stack) or similar serverless
- FFmpeg must be installed in the container image, not system PATH
- Whisper model cached in container, not re-downloaded per job
- ElevenLabs + Kling API keys managed as Modal secrets, not .env
- Job queue / webhook pattern for async renders (Kling can take minutes)

[[reference_remotion_doc_framework]] — Remotion is a separate output format (motion graphics); the FFmpeg assembler handles Kling clip-stitching. Both are SaaS candidates.
