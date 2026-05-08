import React from "react";
import { Composition } from "remotion";
import { DocumentaryTimeline } from "./DocumentaryTimeline";
import { TOTAL_FRAMES } from "./timeline";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AnchorDoc"
        component={DocumentaryTimeline}
        durationInFrames={TOTAL_FRAMES}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
