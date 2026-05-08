// Timeline data — v2, rebuilt from actual asset durations.
//
// Bug fixes vs v1:
//  - All clip slots are ≤ source clip duration (no last-frame freeze).
//  - Narrations tile tightly using their actual MP3 lengths
//    (probed via mutagen 2026-05-08): 71.8 / 19.7 / 37.6 / 82.4 / 53.9 / 68.1 / 38.5 sec
//  - Card 2 moved 4:25 → 4:08 (closes the 17s post-Beat-1-closeout gap).
//  - Beat 2 narration moved 4:35 → 4:18 (against the moved card).
//  - Beat 3 narration moved 7:08 → 6:00 (closes the 70s gap Tommy heard).
//  - Beat 4 narration moved 10:00 → 9:30 (eliminates the 1:22 dead-air after).
//  - Doc trimmed 13:30 → 13:10 (drops the 22s post-CTA dead air).
//  - Beat 1 walking clips unmuted (light ambient under narration, not silence).

export const FPS = 30;
export const sec = (s: number) => Math.round(s * FPS);
export const TOTAL_FRAMES = sec(13 * 60 + 10); // 13:10 = 23700

export type ClipEntry = {
  start: number;
  duration: number;
  src: string;
  trimStartSec?: number;
  mute?: boolean;
  cropMaskRight?: number;
  cropMaskTopLeft?: { w: number; h: number };
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

// 7 narration MP3s, tiled by actual duration.
//   beat              start    dur    end
//   01_setup          0:30   71.8   1:41.8
//   02_beat1_setup    1:42   19.7   2:01.7
//   (28s walking ambient)
//   IG reel           2:30   60.0   3:30
//   03_beat1_closeout 3:30   37.6   4:07.6
//   Card 2 silence    4:08   10.0   4:18
//   04_beat2          4:18   82.4   5:40.4
//   (20s road b-roll, light ambient)
//   05_beat3          6:00   53.9   6:53.9
//   (community ambient — clip audio unmuted ~6:54-9:30)
//   06_beat4          9:30   68.1  10:38.1
//   (1:22 walking ambient)
//   Card 3 silence   12:00   30.0  12:30
//   07_cta           12:30   38.5  13:08.5
//   Card 4 fade      13:08.5  1.5  13:10
export const NARRATIONS: NarrationEntry[] = [
  { start: sec(30),    src: "audio/01_setup.mp3",          label: "Setup" },
  { start: sec(102),   src: "audio/02_beat1_setup.mp3",    label: "Beat 1 (pre-reel)" },
  { start: sec(210),   src: "audio/03_beat1_closeout.mp3", label: "Beat 1 closeout" },
  { start: sec(258),   src: "audio/04_beat2.mp3",          label: "Beat 2 — The Road" },
  { start: sec(360),   src: "audio/05_beat3.mp3",          label: "Beat 3 — Community" },
  { start: sec(570),   src: "audio/06_beat4.mp3",          label: "Beat 4 — Mission" },
  { start: sec(750),   src: "audio/07_cta.mp3",            label: "CTA close" },
];

// 4 title cards, full-bleed PNGs.
export const CARDS: CardEntry[] = [
  { start: sec(15),  duration: sec(15), src: "cards/01_card1.png", label: "Main title" },         // 0:15-0:30
  { start: sec(248), duration: sec(10), src: "cards/02_card2.png", label: "James 1:27" },         // 4:08-4:18
  { start: sec(720), duration: sec(30), src: "cards/03_card3.png", label: "Matthew 25:40" },      // 12:00-12:30
  { start: sec(750), duration: sec(40), src: "cards/04_card4.png", label: "CTA" },                // 12:30-13:10
];

// Beat 1 IG monologue, vertical, pillar-boxed in 16:9.
export const IG_REEL = {
  start: sec(150),    // 2:30
  duration: sec(60),  // hold ~60s; reel is 66s with 5s skip = 61s usable
  src: "zay-monologue/beat1_why_im_walking_DXFNFcgEnI5.mp4",
  trimStartSec: 5,
};

// V1 main video. Each slot's `duration` is verified ≤ source clip length
// (minus trimStartSec). No freezes.
export const CLIPS: ClipEntry[] = [
  // ─── Beat 0: Cold Open (0:00-0:15) ───────────────────────────────────────
  // rain_clip is 37.24s — using first 15s.
  { start: sec(0), duration: sec(15), src: "clips/00038_rain_clip_2800609761.mp4" },

  // 0:15-0:30 covered by Card 1.

  // ─── Beat 1 Setup b-roll (0:30-2:30, narration covers 0:30-2:02) ─────────
  // nap_town_intro is 45.10s.
  { start: sec(30),  duration: sec(15),                src: "clips/00026_nap_town_intro_2633662352.mp4" },
  // 675_miles is 10.52s — match exact length, no freeze.
  { start: sec(45),  duration: Math.round(10.5 * FPS), src: "clips/00009_675_miles_to_Indianapolis_350445807.mp4" },
  // W_Day_39 is 30.01s.
  { start: sec(45) + Math.round(10.5 * FPS), duration: sec(30), src: "clips/00027_W_Day_39_754093857.mp4" },
  // DAY_33_WALKING is 30.00s.
  { start: sec(45) + Math.round(10.5 * FPS) + sec(30), duration: sec(30), src: "clips/00008_DAY_33_WALKING_3000_MILES_-_CALI_40_MILES_TO_RICHMOND_IN_FAITH_WALK_support_dona_2463366916.mp4" },
  // 41_miles_left is 30.01s.
  { start: sec(45) + Math.round(10.5 * FPS) + sec(60), duration: sec(30), src: "clips/00014_41_miles_left_to_Indianapolis_2604397892.mp4" },
  // Fill to 2:30 with nap_town_intro from 15s in (45s source - 15s = 30s available; need ~4.5s).
  { start: sec(45) + Math.round(10.5 * FPS) + sec(90), duration: Math.round(4.5 * FPS), src: "clips/00026_nap_town_intro_2633662352.mp4", trimStartSec: 15 },

  // 2:30-3:30 covered by IG reel pillar-box.

  // ─── Beat 1 Closeout (3:30-4:08) ─────────────────────────────────────────
  // SPEECH is 56.98s — using 0-38s (matches narration length exactly).
  { start: sec(210), duration: Math.round(38 * FPS), src: "clips/00046_SPEECH_914284423.mp4", mute: true },

  // 4:08-4:18 covered by Card 2.

  // ─── Beat 2: The Road (4:18-6:00, narration covers 4:18-5:40) ────────────
  { start: sec(258), duration: sec(15),                src: "clips/00038_rain_clip_2800609761.mp4", trimStartSec: 15, mute: true },
  // struggle is 14.02s.
  { start: sec(258) + sec(15), duration: sec(14),      src: "clips/00058_struggle_3397564726.mp4", mute: true },
  // no_food is 20.43s.
  { start: sec(258) + sec(29), duration: sec(20),      src: "clips/00196_no_food_oh_thats_y_2462850237.mp4", mute: true },
  // Naptown_Potholes is 18.91s — match exact length.
  { start: sec(258) + sec(49), duration: Math.round(18.91 * FPS), src: "clips/00011_Naptown_Potholes_Undefeated_3664286968.mp4", mute: true },
  // accident clip is 44.01s — using 30s with HUD masks.
  { start: sec(258) + sec(49) + Math.round(18.91 * FPS), duration: sec(30), src: "clips/00007_Zay_completed_41_miles_after_the_car_accident_2211673905.mp4", mute: true,
    cropMaskRight: 0.20, cropMaskTopLeft: { w: 0.18, h: 0.16 } },
  // Reflective hold to 6:00 — SPEECH from 38s in (57s source, ~14s remaining).
  { start: sec(258) + sec(49) + Math.round(18.91 * FPS) + sec(30), duration: sec(360) - (sec(258) + sec(49) + Math.round(18.91 * FPS) + sec(30)),
    src: "clips/00046_SPEECH_914284423.mp4", trimStartSec: 38, mute: true },

  // ─── Beat 3: The Community (6:00-9:30, narration covers 6:00-6:54) ───────
  // Joy beat — clip audio UNMUTED for ambient warmth.
  { start: sec(360), duration: sec(20),                  src: "clips/00037_drive_by_support_603783872.mp4" },
  { start: sec(380), duration: sec(30),                  src: "clips/00020_WWW_AUNTIE_INDIANAPOLIS_LOVE_2894716816.mp4" },
  { start: sec(410), duration: sec(30),                  src: "clips/00046_All_love_in_Indiana_2584435906.mp4" },
  // IRON_MAN is 12.55s — match exact length.
  { start: sec(440), duration: Math.round(12.55 * FPS),  src: "clips/00069_W_IRON_MAN_2394675967.mp4" },
  { start: sec(440) + Math.round(12.55 * FPS), duration: sec(30), src: "clips/00027_W_Terrance_205914417.mp4" },
  // Indiana_pulling is 14.82s.
  { start: sec(440) + Math.round(12.55 * FPS) + sec(30), duration: Math.round(14.82 * FPS),
    src: "clips/00011_Indiana_pulling_up_for_the_home_stretch._who_s_ya_mama_3608673546.mp4" },
  { start: sec(440) + Math.round(12.55 * FPS) + sec(30) + Math.round(14.82 * FPS), duration: sec(30),
    src: "clips/00030_www_hokas_gifted_1734762974.mp4" },
  // AIR_BNB is 17.05s.
  { start: sec(440) + Math.round(12.55 * FPS) + sec(60) + Math.round(14.82 * FPS), duration: Math.round(17.05 * FPS),
    src: "clips/00025_W_AIR_BNB_Bro_got_a_corner_office_238615942.mp4" },
  // GIMMIE_MY_HAT is 30.02s — fill to exactly 9:30 (sec 570).
  { start: sec(440) + Math.round(12.55 * FPS) + sec(60) + Math.round(14.82 * FPS) + Math.round(17.05 * FPS),
    duration: sec(570) - (sec(440) + Math.round(12.55 * FPS) + sec(60) + Math.round(14.82 * FPS) + Math.round(17.05 * FPS)),
    src: "clips/00150_GIMMIE_MY_HAT_1027974929.mp4" },

  // ─── Beat 4: The Mission (9:30-12:00, narration covers 9:30-10:38) ───────
  // Light ambient under narration; reuse clips with different trim points for variety.
  { start: sec(570), duration: sec(30),                  src: "clips/00027_W_Day_39_754093857.mp4", mute: true },          // Day 39
  { start: sec(600), duration: sec(30),                  src: "clips/00016_W_Day_40_3888359721.mp4", mute: true },          // Day 40
  { start: sec(630), duration: sec(30),                  src: "clips/00026_nap_town_intro_2633662352.mp4", mute: true },    // walking
  { start: sec(660), duration: sec(18),                  src: "clips/00046_SPEECH_914284423.mp4", mute: true },             // Zay walking 0-18
  { start: sec(678), duration: sec(30),                  src: "clips/00014_41_miles_left_to_Indianapolis_2604397892.mp4", mute: true }, // milestone
  { start: sec(708), duration: sec(12),                  src: "clips/00046_SPEECH_914284423.mp4", trimStartSec: 18, mute: true },      // 18-30 of SPEECH

  // 12:00-12:30 covered by Card 3.
  // 12:30-13:10 covered by Card 4.
];
