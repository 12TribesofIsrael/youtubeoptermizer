import React from "react";
import { Composition } from "remotion";
import { Short } from "./Short";
import { SHORTS, SHORT_DURATION_FRAMES, SHORT_WIDTH, SHORT_HEIGHT } from "./shorts";

export const RemotionRoot: React.FC = () => (
  <>
    {SHORTS.map((config) => (
      <Composition
        key={config.id}
        id={config.id}
        component={Short}
        durationInFrames={SHORT_DURATION_FRAMES}
        fps={30}
        width={SHORT_WIDTH}
        height={SHORT_HEIGHT}
        defaultProps={{ config }}
      />
    ))}
  </>
);
