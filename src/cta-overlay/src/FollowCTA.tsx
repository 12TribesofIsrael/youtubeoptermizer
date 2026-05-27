import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from "remotion";
import { theme } from "./theme";

export type CTAVariant = "reward" | "curiosity" | "social";

const variantText: Record<CTAVariant, string> = {
  reward: "for daily 12 Tribes drops",
  curiosity: "there's more →",
  social: "1K+ walking with us",
};

const variantEmoji: Record<CTAVariant, string> = {
  reward: "🔱",
  curiosity: "",
  social: "",
};

// ─── Drifting gold particle field ─────────────────────────────────────────
const Particles: React.FC = () => {
  const frame = useCurrentFrame();
  const particles = Array.from({ length: 14 }, (_, i) => {
    const seed = i * 137.5;
    const baseX = (seed * 7.3) % 1080;
    const baseY = (seed * 11.7) % 1920;
    const driftX = Math.sin((frame + seed) / 22) * 18;
    const driftY = Math.cos((frame + seed) / 28) * 14;
    const size = 3 + ((i * 3) % 5);
    const opacity = 0.35 + 0.25 * Math.sin((frame + seed) / 18);
    return (
      <div
        key={i}
        style={{
          position: "absolute",
          left: baseX + driftX,
          top: baseY + driftY,
          width: size,
          height: size,
          borderRadius: "50%",
          background: theme.accentGoldGlow,
          boxShadow: `0 0 ${size * 3}px ${theme.accentGoldGlow}`,
          opacity,
        }}
      />
    );
  });
  return <>{particles}</>;
};

// ─── Animated up-arrow pointing to profile pic area ───────────────────────
const PulsingArrow: React.FC = () => {
  const frame = useCurrentFrame();
  const pulse = 1 + 0.12 * Math.sin(frame / 4);
  const opacity = interpolate(frame, [20, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        top: 140,
        left: 0,
        right: 0,
        textAlign: "center",
        fontSize: 110,
        transform: `scale(${pulse})`,
        opacity,
        textShadow: `0 0 30px ${theme.accentGoldGlow}`,
        filter: "drop-shadow(0 4px 12px rgba(0,0,0,0.6))",
      }}
    >
      👆🏿
    </div>
  );
};

// ─── Main FOLLOW + variant text block ─────────────────────────────────────
const TextBlock: React.FC<{ variant: CTAVariant }> = ({ variant }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Spring entrance for FOLLOW
  const followEnter = spring({
    frame,
    fps,
    config: { damping: 12, mass: 0.6, stiffness: 90 },
  });
  const followOpacity = interpolate(followEnter, [0, 1], [0, 1]);
  const followY = interpolate(followEnter, [0, 1], [60, 0]);

  // Variant text slides in slightly delayed
  const subEnter = spring({
    frame: frame - 8,
    fps,
    config: { damping: 14, mass: 0.6, stiffness: 90 },
  });
  const subOpacity = interpolate(subEnter, [0, 1], [0, 1]);
  const subY = interpolate(subEnter, [0, 1], [40, 0]);

  // Breathing glow on FOLLOW text
  const glow = 0.6 + 0.4 * Math.sin(frame / 6);

  const variantStr = variantText[variant];
  const emojiStr = variantEmoji[variant];

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        top: 720,
        textAlign: "center",
        fontFamily: theme.serif,
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          fontSize: 220,
          fontWeight: 900,
          letterSpacing: 12,
          color: theme.accentGold,
          textShadow: `0 0 ${40 * glow}px ${theme.accentGoldGlow}, 0 8px 20px rgba(0,0,0,0.85)`,
          opacity: followOpacity,
          transform: `translateY(${followY}px)`,
          lineHeight: 1,
        }}
      >
        FOLLOW
      </div>
      <div
        style={{
          fontSize: 76,
          fontWeight: 600,
          color: theme.textCream,
          marginTop: 50,
          letterSpacing: 1,
          textShadow: "0 4px 14px rgba(0,0,0,0.9)",
          opacity: subOpacity,
          transform: `translateY(${subY}px)`,
          padding: "0 80px",
        }}
      >
        {variantStr} {emojiStr}
      </div>
    </div>
  );
};

// ─── Backdrop: dark navy with radial warm glow toward center ──────────────
const Backdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 6], [0, 0.92], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 50% 45%, ${theme.bgGradientTo} 0%, ${theme.bgDeep} 70%, rgba(10,14,26,0.85) 100%)`,
        opacity: fadeIn,
      }}
    />
  );
};

// ─── Composition entry point ──────────────────────────────────────────────
export const FollowCTA: React.FC<{ variant: CTAVariant }> = ({ variant }) => {
  return (
    <AbsoluteFill>
      <Backdrop />
      <Particles />
      <PulsingArrow />
      <TextBlock variant={variant} />
    </AbsoluteFill>
  );
};
