# CapCut Shot List — Anchor Doc Assembly Reference

**Sequence settings:** 1920x1080, 30fps, h.264, ~13:30 total runtime
**Color profile:** Rec.709, warm-bias grade
**All paths relative to:** `faith-walk-live/anchor-doc/`

This is the build sheet. Drop assets onto the timeline in this order; the in/out points + durations are pre-computed from `clip-durations.tsv`. Numbers are approximate — adjust ±1s during the music pass.

---

## Track Layout

| Track | Purpose |
|---|---|
| **V1** | Main video — clips, title cards, IG reel |
| **V2** | Overlay b-roll (occasional double-cuts), text lower-thirds |
| **V3** | Brand-identity background (for IG reel pillar-box only) |
| **A1** | Daniel narration (per beat, separate audio files) |
| **A2** | Music bed — single cinematic track underneath |
| **A3** | Clip ambient audio (lowered to -18dB under narration, -10dB during montages) |

---

## Timeline

### Beat 0: Cold Open + Title (0:00–0:30)

| Time | Track | Asset | In→Out | Notes |
|---|---|---|---|---|
| 0:00 | V1 | `clips/00038_rain_clip_2800609761.mp4` | 0:00→0:15 (trim) | Cold open. Mute or low ambient. No narration. |
| 0:00 | A2 | (silence or single low tone) | — | No music in cold open — let it breathe |
| 0:15 | V1 | Card 1 — Main Title (1920x1080) | hold 0:15–0:30 | Generated in DALL-E/ChatGPT |
| 0:15 | A2 | Music bed in (low cinematic tone) | start | Fade up |

### Beat 1 Setup: Who & What (0:30–2:00)

| Time | Track | Asset | In→Out | Notes |
|---|---|---|---|---|
| 0:30 | V1 | `clips/00026_nap_town_intro_2633662352.mp4` | 0:00→0:15 of clip | Walking shot under "On March 26..." |
| 0:30 | A1 | Daniel narration — Setup (1) | full | "On March 26, 2026..." |
| 0:45 | V1 | `clips/00009_675_miles_to_Indianapolis_350445807.mp4` | full | Mile-marker visual under "Three thousand miles..." |
| 1:00 | V1 | `clips/00027_W_Day_39_754093857.mp4` | 0:00→0:15 of clip | Walking under "Eighty-two days later..." |
| 1:18 | V1 | `clips/00008_DAY_33_WALKING_3000_MILES_..._2463366916.mp4` | 0:00→0:15 of clip | Stream-archive overlay during "This is Faith Walk Live" |
| 1:30 | V1 | `clips/00014_41_miles_left_to_Indianapolis_2604397892.mp4` | full | Indiana progress under "Past Pennsylvania, through Ohio..." |
| 1:50 | V1 | Generic walking clip (any 30s+ Day 39 clip) | trim 10s | Hold under "you have to understand why..." |

### Beat 1: The Why (2:00–4:25)

| Time | Track | Asset | In→Out | Notes |
|---|---|---|---|---|
| 2:00 | V1 | `clips/00026_nap_town_intro_2633662352.mp4` | 0:15→0:30 of clip | Daniel narration setup b-roll |
| 2:00 | A1 | Daniel narration — Beat 1 setup | full | "Faith Walk Live started as a question..." |
| 2:30 | V1+V3 | `zay-monologue/beat1_why_im_walking_DXFNFcgEnI5.mp4` | 0:05→0:50 of clip | **Pillar-box treatment.** Center vertical 1080x1920 → fits 540x960 in 1920x1080 frame. V3 = brand-identity background fills sides. |
| 2:30 | A3 | (Zay's audio from reel) | full | Bring up to -3dB — this is the load-bearing audio |
| 2:30 | A1 | (silence — Daniel doesn't talk over Zay) | — | |
| 3:30 | V1 | `clips/00046_SPEECH_914284423.mp4` | mute, use as silent b-roll | Zay walking under "A school. A university..." |
| 3:30 | A1 | Daniel narration — Beat 1 close-out | full | "He's not the first man to walk for his community's children..." |
| 4:25 | V1 | Card 2 — James 1:27 Scripture | hold 4:25–4:35 | Generated in DALL-E/ChatGPT |
| 4:25 | A1 | (silence) | — | Let scripture breathe |
| 4:25 | A2 | Music bed pulls back | — | Quiet under scripture |

### Beat 2: The Road (4:35–7:00)

| Time | Track | Asset | In→Out | Notes |
|---|---|---|---|---|
| 4:35 | V1 | `clips/00038_rain_clip_2800609761.mp4` | 0:15→0:30 of clip | Different segment than cold-open (rain b-roll) |
| 4:35 | A1 | Daniel narration — Beat 2 | full | "There is no romance in walking three thousand miles..." |
| 5:00 | V1 | `clips/00058_struggle_3397564726.mp4` | full (14s) | Explicit fatigue |
| 5:14 | V1 | `clips/00196_no_food_oh_thats_y_2462850237.mp4` | 0:00→0:08 of clip | Top-viewed hardship |
| 5:22 | V1 | `clips/00011_Naptown_Potholes_Undefeated_3664286968.mp4` | full (~18s) | Road conditions |
| 5:40 | V1 | `clips/00007_Zay_completed_41_miles_after_the_car_accident_2211673905.mp4` | ~10s from middle | **VERIFIED 2026-05-06 via keyframe extraction.** Day 39 stream, Greenfield IN, Zay in high-vis safety vest holding PHILLY→CALIFORNIA sign. **CROP REQUIRED:** mask right ~20% (Twitch chat sidebar) + top-left ~15% (Day-39 HUD) — use CapCut crop+scale to tighten on Zay's face. |
| 5:55 | A1 | Daniel narration — "A few weeks in, he was hit by a car..." | sync with V1 above | |
| 6:00 | V1 | `clips/00062_41_on_the_comeback_2893141447.mp4` | trim to 10s | Perseverance after the accident — pair with above |
| 6:30 | V1 | Mile-marker clip (any) | hold 30s | Reflective beat |
| 6:30 | A1 | Daniel — "This is the part of the story you can't fake..." | continue | |
| 6:55 | V1 | (transition to community beat) | — | Crossfade or J-cut into Beat 3 |

### Beat 3: The Community (7:00–10:00)

| Time | Track | Asset | In→Out | Notes |
|---|---|---|---|---|
| 7:00 | A2 | Music bed — swell up (warmer cue) | — | This is the joy beat |
| 7:08 | A1 | Daniel — "And then something started happening..." | full | Sets up the montage |
| 7:15 | V1 | `clips/00037_drive_by_support_603783872.mp4` | full (20s) | LEAD montage clip |
| 7:35 | V1 | `clips/00020_WWW_AUNTIE_INDIANAPOLIS_LOVE_2894716816.mp4` | full (30s) | Auntie sequence start |
| 8:05 | V1 | `clips/00046_All_love_in_Indiana_2584435906.mp4` | 0:00→0:20 of clip | Continue auntie warmth |
| 8:25 | V1 | `clips/00069_W_IRON_MAN_2394675967.mp4` | full (12.5s) | High-energy named brother |
| 8:38 | V1 | `clips/00027_W_Terrance_205914417.mp4` | 0:00→0:15 of clip | Named supporter |
| 8:53 | V1 | `clips/00011_Indiana_pulling_up_for_the_home_stretch._who_s_ya_mama_3608673546.mp4` | full (14s) | Recurring "who's ya mama" refrain |
| 9:07 | V1 | `clips/00030_www_hokas_gifted_1734762974.mp4` | 0:00→0:20 of clip | Shoes gifted |
| 9:27 | V1 | `clips/00025_W_AIR_BNB_Bro_got_a_corner_office_238615942.mp4` | full (17s) | AirBnB lodging |
| 9:44 | V1 | `clips/00150_GIMMIE_MY_HAT_1027974929.mp4` | full (30s, music-sync trim) | END montage on this — joy moment |
| 8:40 | A1 | Daniel narration — Beat 3 close (after montage cuts) | full | "These aren't actors..." — overlap last 60s of montage |

### Beat 4: The Mission (10:00–12:00)

| Time | Track | Asset | In→Out | Notes |
|---|---|---|---|---|
| 10:00 | A2 | Music bed — pull back to gravitas tone | — | |
| 10:00 | V1 | Brand b-roll: faithwalklive.com URL card / banner | hold 0:30 | Generated separately |
| 10:00 | A1 | Daniel narration — Beat 4 | full | "That's why we built faithwalklive.com..." |
| 10:30 | V1 | Channel banner / @AIBIBLEGOSPELS logo | hold 0:15 | Brand wrapper |
| 10:48 | V1 | (return to Zay walking) | various | "Software in service of the calling" |
| 11:10 | V1 | `clips/00027_W_Day_39_754093857.mp4` | 0:00→0:15 | Day 39 milestone |
| 11:25 | V1 | `clips/00016_W_Day_40_3888359721.mp4` | full (30s, trim to 0:10) | Day 40 |
| 11:35 | V1 | Sunset/golden-hour walking shot (any Day 39+ clip) | hold to 12:00 | Hold under "Every step is a brick..." |

### Closing: Scripture + CTA (12:00–13:30)

| Time | Track | Asset | In→Out | Notes |
|---|---|---|---|---|
| 12:00 | V1 | Card 3 — Matthew 25:40 Scripture | hold 12:00–12:30 | Generated in DALL-E/ChatGPT |
| 12:00 | A1 | (silence) | — | |
| 12:00 | A2 | Music bed quiet | — | |
| 12:30 | V1 | Card 4 — CTA Closing | hold 12:30–13:30 | Three-section CTA card |
| 12:30 | A1 | Daniel narration — CTA | full | "If this stirred something in you, three things..." |
| 13:25 | A2 | Music bed fade to silence | — | |
| 13:30 | END | — | — | |

---

## Color Grade Pass (after timeline lock)

- Push warm gold/amber on highlights (+10 saturation on yellows/oranges)
- Lift shadows slightly to maintain face visibility (Zay is melanated — under-grading will lose detail)
- Avoid cool/blue tones — they fight the brand identity
- Apply consistent grade across Twitch clips (which were streamed in varied lighting) and the IG reel

## Subtitle Pass (after color)

- Burn in subtitles for entire doc — gold serif on translucent black band, lower-third
- Verify "Humble Zay" reads correctly (Whisper auto-cap will mangle it — manually correct)
- Keep subtitle font subordinate to title-card font (smaller, less ornate) so they don't compete

## Music Track Suggestion (royalty-free)

- Cinematic-orchestral with sparse piano + low strings
- BPM: ~70 (matches walking pace)
- Look for tracks with a quiet section (Beat 1 + Beat 4) and a swell section (Beat 3)
- YouTube Audio Library: search "documentary cinematic emotional" — pick something with no vocal, no specific cultural genre lean

## Pre-Render QA

- [ ] All 3 cards (title, scripture x2, CTA) render at 1920x1080 with text readable at 480p
- [ ] IG reel pillar-box doesn't crop Zay's face
- [ ] Daniel narration peaks don't clash with music swells
- [ ] Subtitles match audio (no drift)
- [ ] No copyright-claim audio (run through YT Studio "check copyright" before publish)
- [ ] Final export: 1920x1080, 30fps, h.264, ~50–80 Mbps for upload
