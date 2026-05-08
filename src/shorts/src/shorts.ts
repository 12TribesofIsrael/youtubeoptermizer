// Faith Walk Live Shorts — 6 configs, one per Short.
// Each Short is 30 sec @ 30 fps = 900 frames, vertical 1080x1920.

export const FPS = 30;
export const SHORT_DURATION_FRAMES = 900; // 30 sec
export const SHORT_WIDTH = 1080;
export const SHORT_HEIGHT = 1920;
export const sec = (s: number) => Math.round(s * FPS);

export type ClipSegment = {
  src: string;          // staticFile path
  start: number;        // start in frames within the Short timeline
  duration: number;     // in frames
  trimStartSec?: number;// skip first N seconds of source clip
  // Audio: clips default to UNMUTED (clip ambient plays). Only set mute=true
  // when a narration MP3 or other audio track is replacing the clip's audio
  // for that segment. Silence in a 30s mobile-vertical Short reads as broken.
  mute?: boolean;
  // Source aspect — drives the cropping behaviour:
  // - "vertical": already 9:16, render full-bleed
  // - "wide-face-center": 16:9, center-crop on face (default)
  // - "wide-pillarbox": 16:9, scale to fit width with brand bg above/below
  source: "vertical" | "wide-face-center" | "wide-pillarbox";
};

export type TextCue = {
  start: number;        // start frame
  duration: number;     // frames
  text: string;
  position: "top" | "bottom";
  size?: "hook" | "body" | "cta";  // controls font size + weight
};

export type ShortConfig = {
  id: string;           // composition id (e.g. "s1_why")
  fileLabel: string;    // for output filename
  title: string;        // YouTube title
  description: string;  // YouTube description
  clips: ClipSegment[];
  cues: TextCue[];
};

const STANDARD_CTA_DESCRIPTION = `Full documentary on the channel.

🥾 Track the walk live: https://faithwalklive.com
💰 Donate to the school: https://gofund.me/19cf823bc
🎥 Live on Twitch: https://www.twitch.tv/hmblzayy

#AIBibleGospels #FaithWalkLive #HumbleZay #Shorts`;

// ─────────────────────────────────────────────────────────────────────────────
// SHORT 1 — The Why (Beat 1 IG reel excerpt)
// ─────────────────────────────────────────────────────────────────────────────
const s1_why: ShortConfig = {
  id: "s1-why",
  fileLabel: "01-the-why",
  title: "He's walking 3000 miles. Here's why. #FaithWalkLive #Shorts",
  description: `Minister Humble Zay explains why he's walking 3,000 miles from Philadelphia to California — to build a school for at-risk Philly kids.

${STANDARD_CTA_DESCRIPTION}`,
  clips: [
    {
      src: "clips/beat1_why_im_walking_DXFNFcgEnI5.mp4",
      start: 0,
      duration: SHORT_DURATION_FRAMES,
      trimStartSec: 5,
      source: "vertical",
    },
  ],
  cues: [
    { start: 0,        duration: sec(3.5), text: "He's walking 3000 miles", position: "top", size: "hook" },
    { start: sec(3.5), duration: sec(2),   text: "Here's why ↓",            position: "top", size: "hook" },
    { start: sec(26),  duration: sec(4),   text: "Full doc → @AIBIBLEGOSPELS", position: "bottom", size: "cta" },
  ],
};

// ─────────────────────────────────────────────────────────────────────────────
// SHORT 2 — The Hit (Day 19 accident → Day 20 walking again)
// ─────────────────────────────────────────────────────────────────────────────
const s2_hit: ShortConfig = {
  id: "s2-hit",
  fileLabel: "02-the-hit",
  title: "Hit by a car on Day 19. Walking again Day 20. #FaithWalkLive #Shorts",
  description: `Minister Zay was struck by a vehicle on US-40 in Indiana during his 3,000-mile walk. Five days later, he was back on the road.

${STANDARD_CTA_DESCRIPTION}`,
  clips: [
    {
      src: "clips/00007_Zay_completed_41_miles_after_the_car_accident_2211673905.mp4",
      start: 0,
      duration: sec(15),
      trimStartSec: 8, // skip Twitch intro overlay frames
      source: "wide-face-center",
    },
    {
      src: "clips/00062_41_on_the_comeback_2893141447.mp4",
      start: sec(15),
      duration: sec(15),
      source: "wide-face-center",
    },
  ],
  cues: [
    { start: 0,        duration: sec(4),   text: "Hit by a car on Day 19.",     position: "top", size: "hook" },
    { start: sec(15),  duration: sec(4),   text: "Walking again Day 20.",       position: "top", size: "hook" },
    { start: sec(26),  duration: sec(4),   text: "Full doc → @AIBIBLEGOSPELS",  position: "bottom", size: "cta" },
  ],
};

// ─────────────────────────────────────────────────────────────────────────────
// SHORT 3 — The Auntie
// ─────────────────────────────────────────────────────────────────────────────
const s3_auntie: ShortConfig = {
  id: "s3-auntie",
  fileLabel: "03-the-auntie",
  title: "Strangers showing up for him 3000 miles in #FaithWalkLive #Shorts",
  description: `Indianapolis aunties pull up to support Minister Zay during his 3,000-mile walk. The community is showing up at every stop.

${STANDARD_CTA_DESCRIPTION}`,
  clips: [
    {
      src: "clips/00020_WWW_AUNTIE_INDIANAPOLIS_LOVE_2894716816.mp4",
      start: 0,
      duration: SHORT_DURATION_FRAMES,
      source: "wide-face-center",
    },
  ],
  cues: [
    { start: 0,        duration: sec(4),   text: "Strangers showing up for him",     position: "top", size: "hook" },
    { start: sec(4),   duration: sec(2),   text: "Over 600 miles in",                position: "top", size: "hook" },
    { start: sec(26),  duration: sec(4),   text: "Full doc → @AIBIBLEGOSPELS",       position: "bottom", size: "cta" },
  ],
};

// ─────────────────────────────────────────────────────────────────────────────
// SHORT 4 — The Hokas
// ─────────────────────────────────────────────────────────────────────────────
const s4_hokas: ShortConfig = {
  id: "s4-hokas",
  fileLabel: "04-the-hokas",
  title: "Community gifted him new shoes when his blew out #FaithWalkLive #Shorts",
  description: `Halfway through 3,000 miles on foot, Zay's shoes blew out. Within hours, the community gifted him new ones.

${STANDARD_CTA_DESCRIPTION}`,
  clips: [
    {
      src: "clips/00030_www_hokas_gifted_1734762974.mp4",
      start: 0,
      duration: SHORT_DURATION_FRAMES,
      source: "wide-face-center",
    },
  ],
  cues: [
    { start: 0,        duration: sec(4),   text: "His shoes blew out", position: "top", size: "hook" },
    { start: sec(4),   duration: sec(3),   text: "Community gifted him new ones", position: "top", size: "hook" },
    { start: sec(26),  duration: sec(4),   text: "Full doc → @AIBIBLEGOSPELS",  position: "bottom", size: "cta" },
  ],
};

// ─────────────────────────────────────────────────────────────────────────────
// SHORT 5 — The Milestone
// ─────────────────────────────────────────────────────────────────────────────
const s5_milestone: ShortConfig = {
  id: "s5-milestone",
  fileLabel: "05-the-milestone",
  title: "Day 44 of 3000 miles — Indianapolis #FaithWalkLive #Shorts",
  description: `Six weeks into a 3,000-mile walk from Philadelphia to California. Real-time tracker at faithwalklive.com.

${STANDARD_CTA_DESCRIPTION}`,
  clips: [
    {
      src: "clips/00027_W_Day_39_754093857.mp4",
      start: 0,
      duration: sec(15),
      source: "wide-face-center",
    },
    {
      src: "clips/00016_W_Day_40_3888359721.mp4",
      start: sec(15),
      duration: sec(15),
      source: "wide-face-center",
    },
  ],
  cues: [
    { start: 0,        duration: sec(4),   text: "Day 44",                          position: "top", size: "hook" },
    { start: sec(4),   duration: sec(4),   text: "Indianapolis, IN",                position: "top", size: "body" },
    { start: sec(8),   duration: sec(4),   text: "Six weeks in",                    position: "top", size: "body" },
    { start: sec(13),  duration: sec(8),   text: "Track live →\nfaithwalklive.com", position: "bottom", size: "body" },
    { start: sec(26),  duration: sec(4),   text: "Full doc → @AIBIBLEGOSPELS",      position: "bottom", size: "cta" },
  ],
};

// ─────────────────────────────────────────────────────────────────────────────
// SHORT 6 — The Test (struggle montage)
// ─────────────────────────────────────────────────────────────────────────────
const s6_test: ShortConfig = {
  id: "s6-test",
  fileLabel: "06-the-test",
  title: "What it actually takes to walk 3000 miles #FaithWalkLive #Shorts",
  description: `Rain. No food. Potholes. Still walking. The brutal reality of 3,000 miles on foot.

${STANDARD_CTA_DESCRIPTION}`,
  clips: [
    // Note: clips UNMUTED — natural ambient (rain, road noise, Zay self-talk)
    // gives the montage rhythm. Silence in mobile-vertical Shorts reads as
    // broken; only mute when a narration track is replacing clip audio.
    { src: "clips/00038_rain_clip_2800609761.mp4",        start: 0,         duration: sec(7),  source: "wide-face-center" },
    { src: "clips/00058_struggle_3397564726.mp4",         start: sec(7),    duration: sec(7),  source: "wide-face-center" },
    { src: "clips/00196_no_food_oh_thats_y_2462850237.mp4", start: sec(14), duration: sec(6),  source: "wide-face-center" },
    { src: "clips/00011_Naptown_Potholes_Undefeated_3664286968.mp4", start: sec(20), duration: sec(5), source: "wide-face-center" },
    { src: "clips/00062_41_on_the_comeback_2893141447.mp4", start: sec(25), duration: sec(5),  source: "wide-face-center" },
  ],
  cues: [
    { start: 0,        duration: sec(4),   text: "What it takes to walk 3000 miles", position: "top", size: "hook" },
    { start: sec(7),   duration: sec(2),   text: "RAIN",       position: "top", size: "body" },
    { start: sec(9),   duration: sec(4),   text: "FATIGUE",    position: "top", size: "body" },
    { start: sec(14),  duration: sec(4),   text: "NO FOOD",    position: "top", size: "body" },
    { start: sec(20),  duration: sec(3),   text: "POTHOLES",   position: "top", size: "body" },
    { start: sec(23),  duration: sec(2),   text: "Still walking", position: "top", size: "hook" },
    { start: sec(26),  duration: sec(4),   text: "Full doc → @AIBIBLEGOSPELS",  position: "bottom", size: "cta" },
  ],
};

export const SHORTS: ShortConfig[] = [s1_why, s2_hit, s3_auntie, s4_hokas, s5_milestone, s6_test];
