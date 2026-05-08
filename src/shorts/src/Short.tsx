import React from "react";
import {
  AbsoluteFill,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
} from "remotion";
import { ShortConfig, TextCue, ClipSegment } from "./shorts";
import { theme } from "./theme";

// ─── Brand-bg pillar / letterbox treatment ─────────────────────────────────
const BrandBg: React.FC = () => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(ellipse at center, ${theme.bgGradientTo} 0%, ${theme.bgDeep} 80%)`,
    }}
  >
    <div
      style={{
        position: "absolute",
        inset: 0,
        backgroundImage: `radial-gradient(${theme.accentGoldGlow}33 1px, transparent 1px)`,
        backgroundSize: "60px 60px",
        opacity: 0.3,
      }}
    />
  </AbsoluteFill>
);

// ─── Single video clip rendered in 9:16 frame ──────────────────────────────
const ClipBlock: React.FC<{ clip: ClipSegment }> = ({ clip }) => {
  const trimStart = clip.trimStartSec ? Math.round(clip.trimStartSec * 30) : 0;
  const muted = clip.mute ?? false;

  if (clip.source === "vertical") {
    // Source is already 9:16 — render full-bleed.
    return (
      <AbsoluteFill style={{ backgroundColor: "#000" }}>
        <OffthreadVideo
          src={staticFile(clip.src)}
          startFrom={trimStart}
          muted={muted}
          volume={muted ? 0 : 1.0}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>
    );
  }

  if (clip.source === "wide-pillarbox") {
    // 16:9 source scaled to fit 1080 width, with brand bg top + bottom.
    return (
      <>
        <BrandBg />
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
          <div style={{ width: 1080, height: 607 /* 1080 * 9/16 */ }}>
            <OffthreadVideo
              src={staticFile(clip.src)}
              startFrom={trimStart}
              muted={muted}
              volume={muted ? 0 : 1.0}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
          </div>
        </AbsoluteFill>
      </>
    );
  }

  // Default: wide-face-center — center-crop the 16:9 source onto a 9:16 frame
  // by scaling source to fill 1920 height, which means we crop ~67% of the
  // horizontal — keeps faces near center in frame.
  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
      <OffthreadVideo
        src={staticFile(clip.src)}
        startFrom={trimStart}
        muted={muted}
        volume={muted ? 0 : 1.0}
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          height: "100%",
          width: "auto",
          transform: "translate(-50%, -50%)",
          objectFit: "cover",
        }}
      />
    </AbsoluteFill>
  );
};

// ─── Animated text cue overlay ─────────────────────────────────────────────
const TextOverlay: React.FC<{ cue: TextCue }> = ({ cue }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Spring entrance: slide up + fade in over first 0.4s.
  const enter = spring({ frame, fps, config: { damping: 70, stiffness: 180 } });
  const opacity = interpolate(enter, [0, 1], [0, 1]);
  const translateY = interpolate(enter, [0, 1], [30, 0]);

  // Fade out last 0.3s.
  const exitStart = cue.duration - 9;
  const exitOpacity = interpolate(frame, [exitStart, cue.duration], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const fontSize = cue.size === "hook" ? 92 : cue.size === "cta" ? 64 : 78;
  const fontWeight = cue.size === "hook" ? 800 : cue.size === "cta" ? 700 : 700;
  const color = cue.size === "cta" ? theme.accentGold : theme.textCream;

  const containerStyle: React.CSSProperties = {
    position: "absolute",
    left: 60,
    right: 60,
    [cue.position === "top" ? "top" : "bottom"]: 200,
    opacity: opacity * exitOpacity,
    transform: `translateY(${cue.position === "top" ? translateY : -translateY}px)`,
    textAlign: "center",
    pointerEvents: "none",
  };

  return (
    <div style={containerStyle}>
      <div
        style={{
          display: "inline-block",
          padding: "32px 48px",
          background: "rgba(0, 0, 0, 0.78)",
          color,
          fontFamily: theme.serif,
          fontSize,
          fontWeight,
          lineHeight: 1.15,
          letterSpacing: cue.size === "hook" ? -1 : 0,
          textShadow: "0 4px 12px rgba(0, 0, 0, 0.85)",
          borderLeft: `6px solid ${theme.accentGold}`,
          borderRadius: 6,
          maxWidth: "100%",
          whiteSpace: "pre-line",
        }}
      >
        {cue.text}
      </div>
    </div>
  );
};

// ─── The Short composition ────────────────────────────────────────────────
export const Short: React.FC<{ config: ShortConfig }> = ({ config }) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Layer 1: video clips */}
      {config.clips.map((clip, i) => (
        <Sequence key={`clip-${i}`} from={clip.start} durationInFrames={clip.duration}>
          <ClipBlock clip={clip} />
        </Sequence>
      ))}

      {/* Layer 2: text cues */}
      {config.cues.map((cue, i) => (
        <Sequence key={`cue-${i}`} from={cue.start} durationInFrames={cue.duration}>
          <TextOverlay cue={cue} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
