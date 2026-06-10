"use client";

import dynamic from "next/dynamic";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";

import MissionPanel from "@/components/MissionPanel";
import StoryIntro from "@/components/StoryIntro";
import type { MapNode } from "@/components/GameCanvas";
import { getAdventure, getProgress } from "@/lib/api";
import type { Adventure, Progress, SubmissionResult } from "@/lib/types";

// Phaser touches `window`; never render it on the server.
const GameCanvas = dynamic(() => import("@/components/GameCanvas"), { ssr: false });

export default function PlayPage() {
  const params = useParams<{ id: string }>();
  const adventureId = Number(params.id);

  const [adventure, setAdventure] = useState<Adventure | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [showIntro, setShowIntro] = useState(true);
  const [activeMissionId, setActiveMissionId] = useState<string | null>(null);
  const [error, setError] = useState("");

  const refreshProgress = useCallback(async () => {
    try {
      setProgress(await getProgress(adventureId));
    } catch (err) {
      // A failed refresh must not strand the player on a stale map.
      setError(err instanceof Error ? err.message : String(err));
    }
  }, [adventureId]);

  useEffect(() => {
    if (!Number.isFinite(adventureId)) return;
    Promise.all([getAdventure(adventureId), getProgress(adventureId)])
      .then(([adv, prog]) => {
        setAdventure(adv);
        setProgress(prog);
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, [adventureId]);

  const nodes: MapNode[] = useMemo(() => {
    if (!adventure || !progress) return [];
    const statusById = new Map(progress.missions.map((m) => [m.mission_id, m.status]));
    return adventure.missions.map((m) => ({
      missionId: m.mission_id,
      title: m.title,
      status: statusById.get(m.mission_id) ?? "locked",
    }));
  }, [adventure, progress]);

  function onMissionResult(result: SubmissionResult) {
    if (result.passed) void refreshProgress();
  }

  if (error) {
    return (
      <main className="container">
        <div className="error-banner">Could not load this adventure: {error}</div>
      </main>
    );
  }
  if (!adventure || !progress) {
    return (
      <main className="container">
        <p className="subtitle">Loading your world…</p>
      </main>
    );
  }

  const arc = adventure.story_arc;
  const activeMission = adventure.missions.find((m) => m.mission_id === activeMissionId);
  const finished = progress.completed_count === progress.total_count;

  return (
    <main className="container">
      <div className="play-header">
        <div>
          <span className="badge">{arc.theme}</span>
          <h1 style={{ display: "inline", marginLeft: "0.3rem" }}>{arc.story_title}</h1>
        </div>
        <span className="progress">
          {progress.completed_count} / {progress.total_count} missions complete
        </span>
      </div>

      {finished ? (
        <div className="card finale">
          <h2>🏆 {arc.main_goal}</h2>
          <p>{arc.final_challenge.description}</p>
          <p className="subtitle">
            You used: {arc.final_challenge.concepts_combined.join(", ")} — the next chapter
            of the course continues from here.
          </p>
        </div>
      ) : (
        <>
          <GameCanvas theme={arc.theme} nodes={nodes} onEnterMission={setActiveMissionId} />
          <p className="hud-tip">
            Move with the arrow keys. Walk to a glowing node and press SPACE — or click it —
            to start a mission.
          </p>
        </>
      )}

      {showIntro && <StoryIntro arc={arc} onBegin={() => setShowIntro(false)} />}

      {activeMission && (
        <MissionPanel
          adventureId={adventureId}
          mission={activeMission}
          arc={arc}
          onClose={() => {
            setActiveMissionId(null);
            void refreshProgress();
          }}
          onResult={onMissionResult}
        />
      )}
    </main>
  );
}
