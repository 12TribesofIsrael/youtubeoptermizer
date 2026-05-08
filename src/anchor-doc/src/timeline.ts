// Timeline data — derived from faith-walk-live/anchor-doc/capcut-shot-list.md.
// All paths are relative to public/ (resolved via staticFile() at render time).
//
// Timestamps come from the shot list. They were planned against the narration
// script's pacing; if a narration MP3 runs slightly long/short, individual
// clip durations may need ±1s nudges in this file.

export const FPS = 30;
export const sec = (s: number) => Math.round(s * FPS);
export const TOTAL_FRAMES = sec(13 * 60 + 30); // 13:30 = 24300

export type ClipEntry = {
  start: number;       // frame
  duration: number;    // frames
  src: string;
  trimStartSec?: number; // skip first N seconds of the source clip
  mute?: boolean;        // mute the clip's own audio
  cropMaskRight?: number;// 0-1 fraction; mask right edge (e.g., Twitch chat sidebar)
  cropMaskTopLeft?: { w: number; h: number }; // mask top-left HUD overlay
};

export type CardEntry = {
  start: number;
  duration: number;
  src: string;
  label: string;
};

export type NarrationEntry = {
  start: number;
  src: string;
  label: string;
};

// Daniel narration — 7 MP3s, one per beat.
// Lower volume (-12dB ish in CapCut speak ≈ 0.25 in Remotion gain) when clip
// audio is also playing; full volume when no clip audio competes. For v1 we
// play narration at 1.0 and clip audio at 0.2 except where noted.
export const NARRATIONS: NarrationEntry[] = [
  { start: sec(30),  src: "audio/01_setup.mp3",          label: "Beat 1 setup" },        // 0:30
  { start: sec(120), src: "audio/02_beat1_setup.mp3",    label: "Beat 1 (pre-reel)" },   // 2:00
  { start: sec(210), src: "audio/03_beat1_closeout.mp3", label: "Beat 1 closeout" },     // 3:30
  { start: sec(275), src: "audio/04_beat2.mp3",          label: "Beat 2 — The Road" },   // 4:35
  { start: sec(428), src: "audio/05_beat3.mp3",          label: "Beat 3 — Community" },  // 7:08
  { start: sec(600), src: "audio/06_beat4.mp3",          label: "Beat 4 — Mission" },    // 10:00
  { start: sec(750), src: "audio/07_cta.mp3",            label: "CTA close" },           // 12:30
];

// Title cards — 4 PNGs at fixed timestamps.
export const CARDS: CardEntry[] = [
  { start: sec(15),  duration: sec(15), src: "cards/01_card1.png", label: "Main title" },                   // 0:15-0:30
  { start: sec(265), duration: sec(10), src: "cards/02_card2.png", label: "James 1:27" },                   // 4:25-4:35
  { start: sec(720), duration: sec(30), src: "cards/03_card3.png", label: "Matthew 25:40" },                // 12:00-12:30
  { start: sec(750), duration: sec(60), src: "cards/04_card4.png", label: "CTA close" },                    // 12:30-13:30
];

// Beat 1 IG monologue — vertical 1080x1920, pillar-boxed in 16:9 frame.
// Plays its own audio (Zay talking — load-bearing). Narration silent here.
export const IG_REEL = {
  start: sec(150),       // 2:30
  duration: sec(60),     // hold ~60s; reel is 66s, in-point 0:05, out-point 1:05
  src: "zay-monologue/beat1_why_im_walking_DXFNFcgEnI5.mp4",
  trimStartSec: 5,
};

// Main video (V1) clips. Order follows shot list. Where the shot list has
// gaps in V1 (during cards, during the IG reel), no entry is needed —
// the card or IG reel covers that frame range. Audio gain in v1 stays at
// 0.2 for clip ambient under narration, 1.0 elsewhere.
export const CLIPS: ClipEntry[] = [
  // ─── Beat 0: Cold Open (0:00-0:15) ───────────────────────────────────────
  { start: sec(0), duration: sec(15), src: "clips/00038_rain_clip_2800609761.mp4", mute: false },

  // ─── 0:15-0:30 covered by Card 1 ───

  // ─── Beat 1 Setup: Who & What (0:30-2:00) ────────────────────────────────
  { start: sec(30),  duration: sec(15), src: "clips/00026_nap_town_intro_2633662352.mp4", mute: true },
  { start: sec(45),  duration: sec(15), src: "clips/00009_675_miles_to_Indianapolis_350445807.mp4", mute: true },
  { start: sec(60),  duration: sec(18), src: "clips/00027_W_Day_39_754093857.mp4", mute: true },
  { start: sec(78),  duration: sec(12), src: "clips/00008_DAY_33_WALKING_3000_MILES_-_CALI_40_MILES_TO_RICHMOND_IN_FAITH_WALK_support_dona_2463366916.mp4", mute: true },
  { start: sec(90),  duration: sec(20), src: "clips/00014_41_miles_left_to_Indianapolis_2604397892.mp4", mute: true },
  { start: sec(110), duration: sec(10), src: "clips/00026_nap_town_intro_2633662352.mp4", trimStartSec: 25, mute: true },

  // ─── Beat 1: The Why (2:00-2:30 b-roll, 2:30-3:30 IG reel, 3:30-4:25 closeout) ───
  { start: sec(120), duration: sec(30), src: "clips/00026_nap_town_intro_2633662352.mp4", trimStartSec: 30, mute: true },
  // 2:30-3:30 — IG_REEL handles this range (pillar-boxed)
  { start: sec(210), duration: sec(55), src: "clips/00046_SPEECH_914284423.mp4", mute: true },

  // ─── 4:25-4:35 covered by Card 2 ───

  // ─── Beat 2: The Road (4:35-7:00) ────────────────────────────────────────
  { start: sec(275), duration: sec(15), src: "clips/00038_rain_clip_2800609761.mp4", trimStartSec: 15, mute: true },
  { start: sec(290), duration: sec(14), src: "clips/00058_struggle_3397564726.mp4", mute: true },
  { start: sec(304), duration: sec(8),  src: "clips/00196_no_food_oh_thats_y_2462850237.mp4", mute: true },
  { start: sec(312), duration: sec(18), src: "clips/00011_Naptown_Potholes_Undefeated_3664286968.mp4", mute: true },
  { start: sec(330), duration: sec(20), src: "clips/00007_Zay_completed_41_miles_after_the_car_accident_2211673905.mp4", mute: true,
    cropMaskRight: 0.20, cropMaskTopLeft: { w: 0.18, h: 0.16 } },
  { start: sec(350), duration: sec(10), src: "clips/00062_41_on_the_comeback_2893141447.mp4", mute: true },
  { start: sec(360), duration: sec(60), src: "clips/00014_41_miles_left_to_Indianapolis_2604397892.mp4", mute: true }, // reflective hold

  // ─── Beat 3: The Community (7:00-10:00) ──────────────────────────────────
  // Joy beat — keep clip audio audible (mute: false) for ambient warmth.
  { start: sec(420), duration: sec(20), src: "clips/00037_drive_by_support_603783872.mp4" },
  { start: sec(440), duration: sec(30), src: "clips/00020_WWW_AUNTIE_INDIANAPOLIS_LOVE_2894716816.mp4" },
  { start: sec(470), duration: sec(20), src: "clips/00046_All_love_in_Indiana_2584435906.mp4" },
  { start: sec(490), duration: sec(13), src: "clips/00069_W_IRON_MAN_2394675967.mp4" },
  { start: sec(503), duration: sec(15), src: "clips/00027_W_Terrance_205914417.mp4" },
  { start: sec(518), duration: sec(14), src: "clips/00011_Indiana_pulling_up_for_the_home_stretch._who_s_ya_mama_3608673546.mp4" },
  { start: sec(532), duration: sec(20), src: "clips/00030_www_hokas_gifted_1734762974.mp4" },
  { start: sec(552), duration: sec(17), src: "clips/00025_W_AIR_BNB_Bro_got_a_corner_office_238615942.mp4" },
  { start: sec(569), duration: sec(31), src: "clips/00150_GIMMIE_MY_HAT_1027974929.mp4" },

  // ─── Beat 4: The Mission (10:00-12:00) ───────────────────────────────────
  { start: sec(600), duration: sec(70), src: "clips/00027_W_Day_39_754093857.mp4", mute: true }, // brand b-roll stand-in
  { start: sec(670), duration: sec(15), src: "clips/00027_W_Day_39_754093857.mp4", trimStartSec: 14, mute: true },
  { start: sec(685), duration: sec(10), src: "clips/00016_W_Day_40_3888359721.mp4", mute: true },
  { start: sec(695), duration: sec(25), src: "clips/00027_W_Day_39_754093857.mp4", trimStartSec: 5, mute: true }, // sunset hold

  // ─── 12:00-13:30 covered by Cards 3 + 4 ───
];
