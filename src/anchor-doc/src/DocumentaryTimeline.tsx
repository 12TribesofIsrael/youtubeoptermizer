import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { CARDS, CLIPS, FPS, IG_REEL, NARRATIONS, TOTAL_FRAMES } from "./timeline";
import { theme } from "./theme";
import subtitlesData from "./subtitles.json";

type Cue = { start: number; end: number; text: string };
const SUBTITLES: Cue[] = subtitlesData as Cue[];

// ─── Single clip on the V1 main track ──────────────────────────────────────
const ClipBlock: React.FC<{
  src: string;
  trimStartSec?: number;
  mute?: boolean;
  cropMaskRight?: number;
  cropMaskTopLeft?: { w: number; h: number };
}> = ({ src, trimStartSec, mute, cropMaskRight, cropMaskTopLeft }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      <OffthreadVideo
        src={staticFile(src)}
        startFrom={trimStartSec ? Math.round(trimStartSec * 30) : 0}
        muted={mute ?? false}
        volume={mute ? 0 : 0.25}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />
      {/* HUD masks for the accident clip — cover Twitch chat sidebar + Day 39 HUD */}
      {cropMaskRight && (
        <div
          style={{
            position: "absolute",
            right: 0,
            top: 0,
            bottom: 0,
            width: `${cropMaskRight * 100}%`,
            backgroundColor: "#000",
          }}
        />
      )}
      {cropMaskTopLeft && (
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            width: `${cropMaskTopLeft.w * 100}%`,
            height: `${cropMaskTopLeft.h * 100}%`,
            backgroundColor: "#000",
          }}
        />
      )}
    </AbsoluteFill>
  );
};

// ─── IG reel pillar-box treatment (vertical centered with brand bg sides) ──
const IgReelPillarbox: React.FC = () => {
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at center, ${theme.bgGradientTo} 0%, ${theme.bgDeep} 70%)`,
      }}
    >
      {/* Sparse golden particle effect via box-shadow stack — cheap brand cue */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `radial-gradient(${theme.accentGoldGlow}22 1px, transparent 1px)`,
          backgroundSize: "80px 80px",
          opacity: 0.25,
        }}
      />
      {/* Centered vertical clip — 1080x1920 source fitted to canvas height */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: "translate(-50%, -50%)",
          width: 608, // (1080/1920) * 1080 — letterbox calc to fit height
          height: 1080,
          overflow: "hidden",
        }}
      >
        <OffthreadVideo
          src={staticFile(IG_REEL.src)}
          startFrom={Math.round((IG_REEL.trimStartSec ?? 0) * 30)}
          volume={1.0}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </div>
      {/* Subtle gold serif watermark on each side */}
      <div
        style={{
          position: "absolute",
          left: 60,
          top: "50%",
          transform: "translateY(-50%) rotate(-90deg) translateX(50%)",
          color: theme.accentGold,
          fontFamily: theme.serif,
          fontSize: 24,
          letterSpacing: 8,
          opacity: 0.5,
        }}
      >
        FAITH WALK LIVE
      </div>
      <div
        style={{
          position: "absolute",
          right: 60,
          top: "50%",
          transform: "translateY(-50%) rotate(90deg) translateX(-50%)",
          color: theme.accentGold,
          fontFamily: theme.serif,
          fontSize: 24,
          letterSpacing: 8,
          opacity: 0.5,
        }}
      >
        AI BIBLE GOSPELS
      </div>
    </AbsoluteFill>
  );
};

// ─── Subtitle overlay ──────────────────────────────────────────────────────
// Looks up the active cue at the current frame and renders it lower-third on
// a translucent black band. Gold serif on dark, smaller than card-card text.
const Subtitles: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  // Suppress subs during full-bleed card overlays — cards carry their own text.
  const onCard = CARDS.some(
    (card) => frame >= card.start && frame < card.start + card.duration
  );
  if (onCard) return null;
  const active = SUBTITLES.find((c) => t >= c.start && t <= c.end);
  if (!active) return null;
  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: 60,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          maxWidth: "80%",
          padding: "16px 32px",
          background: "rgba(0, 0, 0, 0.65)",
          color: theme.textCream,
          fontFamily: theme.serif,
          fontSize: 36,
          lineHeight: 1.3,
          textAlign: "center",
          textShadow: "0 2px 4px rgba(0,0,0,0.85)",
          borderRadius: 4,
        }}
      >
        {active.text}
      </div>
    </div>
  );
};

// ─── Card overlay (full-bleed PNG) ─────────────────────────────────────────
const CardOverlay: React.FC<{ src: string }> = ({ src }) => (
  <AbsoluteFill style={{ backgroundColor: "#000" }}>
    <Img
      src={staticFile(src)}
      style={{
        width: "100%",
        height: "100%",
        objectFit: "contain",
      }}
    />
  </AbsoluteFill>
);

// ─── The full timeline composition ─────────────────────────────────────────
export const DocumentaryTimeline: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Layer 1: V1 main video — clips in shot-list order */}
      {CLIPS.map((clip, i) => (
        <Sequence key={`clip-${i}`} from={clip.start} durationInFrames={clip.duration}>
          <ClipBlock
            src={clip.src}
            trimStartSec={clip.trimStartSec}
            mute={clip.mute}
            cropMaskRight={clip.cropMaskRight}
            cropMaskTopLeft={clip.cropMaskTopLeft}
          />
        </Sequence>
      ))}

      {/* Layer 2: Beat 1 IG reel (pillar-boxed) — overlays clips during 2:30-3:30 */}
      <Sequence from={IG_REEL.start} durationInFrames={IG_REEL.duration}>
        <IgReelPillarbox />
      </Sequence>

      {/* Layer 3: Cards (highest visual priority — overlay clips at fixed times) */}
      {CARDS.map((card, i) => (
        <Sequence key={`card-${i}`} from={card.start} durationInFrames={card.duration}>
          <CardOverlay src={card.src} />
        </Sequence>
      ))}

      {/* Layer 4: A1 Daniel narration — separate audio per beat */}
      {NARRATIONS.map((n, i) => (
        <Sequence key={`narr-${i}`} from={n.start} durationInFrames={TOTAL_FRAMES - n.start}>
          <Audio src={staticFile(n.src)} volume={1.0} />
        </Sequence>
      ))}

      {/* Layer 5: Burned-in subtitles (visible everywhere except over cards) */}
      <Subtitles />
    </AbsoluteFill>
  );
};
