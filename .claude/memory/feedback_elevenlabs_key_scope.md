---
name: ElevenLabs API key scope — TTS works, user_read doesn't
description: The shared ELEVENLABS_API_KEY in ai-bible-gospels/.env is TTS-scoped only; subscription/balance probes will 401 even when credits are available
type: feedback
originSessionId: 22dbbefd-de40-46eb-b5d9-138852773417
---
The `ELEVENLABS_API_KEY` in `ai-bible-gospels/.env` (which youtubeoptermizer falls back to) has TTS permissions but lacks `user_read`. Calls to `GET /v1/user/subscription` return `401 missing_permissions`.

**Why:** Older ElevenLabs keys can be issued with restricted scopes. This particular key was provisioned for production TTS, not introspection.

**How to apply:**
- Don't waste a turn probing `/v1/user` or `/v1/user/subscription` to check credit balance — it'll always 401.
- To verify the key actually works after a credit top-up or a new session, send a tiny TTS request directly: `POST /v1/text-to-speech/onwK4e9ZLuTAKqWW03F9` with body `{"text":"Hello.","model_id":"eleven_multilingual_v2"}`. 200 = key + voice + credits all working. 401 quota_exceeded = credits gone. See `scripts/probe-elevenlabs-tts.py`.
- If user wants a real balance dashboard, send them to elevenlabs.io directly — there's no API path with this key.
