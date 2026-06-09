"use client";

import type { StoryArc } from "@/lib/types";

interface Props {
  arc: StoryArc;
  onBegin: () => void;
}

export default function StoryIntro({ arc, onBegin }: Props) {
  return (
    <div className="overlay">
      <div className="panel">
        <span className="badge">{arc.theme}</span>
        <span className="badge">{arc.course_topic}</span>
        <h1>{arc.story_title}</h1>
        <div className="story-block">
          <p>
            <strong>You are:</strong> {arc.protagonist_role}
          </p>
          <p>{arc.world_description}</p>
          <p>{arc.central_conflict}</p>
          <p>
            <strong>Your goal:</strong> {arc.main_goal}
          </p>
        </div>
        <div className="mentor-line">
          <strong>{arc.mentor_character.name}</strong> ({arc.mentor_character.role}) will
          guide you — {arc.mentor_character.personality}
        </div>
        <button onClick={onBegin}>Begin</button>
      </div>
    </div>
  );
}
