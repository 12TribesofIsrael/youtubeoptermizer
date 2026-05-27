import React from "react";
import { Composition } from "remotion";
import { FollowCTA, CTAVariant } from "./FollowCTA";

const WIDTH = 1080;
const HEIGHT = 1920;
const FPS = 30;
const DURATION = 60;

const variants: CTAVariant[] = ["reward", "curiosity", "social"];

export const RemotionRoot: React.FC = () => (
  <>
    {variants.map((variant) => (
      <Composition
        key={`cta-${variant}`}
        id={`cta-${variant}`}
        component={FollowCTA}
        durationInFrames={DURATION}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
        defaultProps={{ variant }}
      />
    ))}
  </>
);
