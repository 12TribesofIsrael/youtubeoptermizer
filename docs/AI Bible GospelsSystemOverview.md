AI Bible Gospels — System Overview
What This Is
A personal AI video production platform that turns text (Bible scripture or custom scripts) into fully rendered cinematic videos using AI services. It's a Python/FastAPI web app deployed on Modal.com.

What It Does
Three pipelines, two in production:

1. Biblical Cinematic Pipeline (Production)
Input: KJV Bible scripture text
Process: Clean text → Claude AI generates cinematic scene descriptions → FLUX Pro generates images → Kling AI animates images into video clips → JSON2Video assembles final MP4 with ElevenLabs narration + subtitles
Output: A cinematic narrated video of Bible chapters
Cost: ~$4.50–7.00/video
2. Custom Script Pipeline (Production)
Input: Any script or concept text
Process: Same AI pipeline (Claude → FLUX → Kling → JSON2Video) but with dynamic scene count
Output: A narrated video from arbitrary scripts
3. General AI Movie Pipeline (Reference/Legacy)
Uses OpenAI GPT-4o + TTS instead of Claude/ElevenLabs
Gradio UI instead of FastAPI
Tech Stack
Layer	Tech
Web server	FastAPI + vanilla HTML/JS frontend
Scene generation	Claude AI (Anthropic API)
Image generation	FLUX Pro via fal.ai
Video animation	Kling AI (v1.6–v3.0 Pro) via fal.ai
Narration	ElevenLabs (via JSON2Video)
Video assembly	JSON2Video API
Post-production	FFmpeg (intro/outro, logo overlay)
YouTube upload	Google OAuth2 API
Hosting	Modal.com (serverless containers)
State persistence	JSON files on Modal Volume
Key Capabilities
Scene editing — Users can review/edit AI-generated scenes before spending render credits
Auto-split — Long chapters (900+ words) automatically split into Part 1/Part 2
Stop/Resume — Cancel mid-render, retry from last completed scene
Fix Scenes — Regenerate specific scenes without redoing the whole video
Preview-first fixes — Preview FLUX+Kling output before committing to a full render
Post-production — FFmpeg adds intro/outro clips, logo watermark, background music
YouTube upload — One-click upload with auto-generated title/description/thumbnail
Render history — Browse and reload past renders
Architecture

Unified web app at http://localhost:8000 (or Modal URL)
├── /           → Scripture Mode (Biblical pipeline)
├── /custom     → Custom Script Mode
├── /api/clean  → Text processor
├── /v9/api/*   → Biblical pipeline routes (generate-scenes, generate-video, status, retry, fix, stop, history)
├── /custom/api/* → Custom script routes (same pattern)
└── /api/render/* → Post-production (FFmpeg, local only)
Key Entry Points
File	Role
modal_app.py	Modal.com deployment entry point
workflows/biblical-cinematic/server/app.py	FastAPI main server
workflows/biblical-cinematic/server/biblical_pipeline.py	Biblical pipeline router
workflows/custom-script/router.py	Custom script pipeline router
External Services Required
FAL_KEY, JSON2VIDEO_API_KEY, ANTHROPIC_API_KEY — plus optional APP_USERNAME/APP_PASSWORD for Basic Auth on Modal.

In Short
It's a text-to-cinematic-video pipeline — primarily for Bible content but extensible to any script — orchestrated through a web UI with scene-level editing, cost controls (stop/retry/fix), and end-to-end automation from raw text to YouTube upload.