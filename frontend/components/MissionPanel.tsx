"use client";

/**
 * The mission screen: story context -> teaching -> task -> editor -> run.
 * Code runs locally in Pyodide (sandboxed worker, hard timeout); the verdict
 * is reported to the backend, which answers with narrative + technical
 * feedback, escalating hints and, after repeated failures, remediation.
 */
import { useEffect, useState } from "react";

import CodeEditor from "./CodeEditor";
import { submitAttempt } from "@/lib/api";
import { runPython, warmUp } from "@/lib/pyodideRunner";
import type { Mission, RunResult, StoryArc, SubmissionResult } from "@/lib/types";

interface Props {
  adventureId: number;
  mission: Mission;
  arc: StoryArc;
  onClose: () => void;
  onResult: (result: SubmissionResult) => void;
}

export default function MissionPanel({ adventureId, mission, arc, onClose, onResult }: Props) {
  const [code, setCode] = useState(mission.starter_code);
  const [running, setRunning] = useState(false);
  const [run, setRun] = useState<RunResult | null>(null);
  const [submission, setSubmission] = useState<SubmissionResult | null>(null);
  // Hints are opt-in (desirable difficulties: struggle before help —
  // see research/learning/). Reveal resets on every new attempt.
  const [hintRevealed, setHintRevealed] = useState(false);
  const [error, setError] = useState("");

  // Hide the Pyodide cold start behind the student's reading time.
  useEffect(() => warmUp(), []);

  async function onRun() {
    setRunning(true);
    setError("");
    try {
      const result = await runPython(code, mission.hidden_tests);
      setRun(result);
      const verdict = await submitAttempt(adventureId, mission.mission_id, code, result);
      setSubmission(verdict);
      setHintRevealed(false);
      onResult(verdict);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setRunning(false);
    }
  }

  const mentor = arc.mentor_character.name;
  const passed = submission?.passed ?? false;

  return (
    <div className="overlay">
      <div className="panel">
        <div className="play-header">
          <div>
            <span className="badge">{mission.module}</span>
            <span className="badge">difficulty {mission.difficulty}</span>
            <h2 style={{ margin: "0.4rem 0 0" }}>{mission.title}</h2>
          </div>
          <button className="ghost" onClick={onClose}>
            ← back to map
          </button>
        </div>

        <div className="mission-grid">
          <div>
            <div className="story-block">
              <p style={{ color: "var(--muted)" }}>{mission.story_context.previous_state}</p>
              <p>{mission.story_context.current_problem}</p>
              <div className="mentor-line">
                {mentor}: “{mission.story_context.why_this_matters}”
              </div>
              <p className="stakes">⚠ {mission.story_context.narrative_stakes}</p>
            </div>

            <details className="explain">
              <summary>
                📘 {mentor} explains: {mission.learning_objective}
              </summary>
              <p className="explain-text">{mission.concept_explanation}</p>
            </details>

            <div className="task-box">
              <strong>Your task</strong>
              <p style={{ margin: "0.4rem 0 0" }}>{mission.student_task}</p>
            </div>

            {submission && !passed && submission.hint && !hintRevealed && (
              <button className="secondary" onClick={() => setHintRevealed(true)}>
                💡 Ask {mentor} for a hint
              </button>
            )}

            {submission && !passed && submission.hint && hintRevealed && (
              <div className="hint-box">
                💡 <strong>Hint {submission.hint_level}:</strong> {submission.hint}
              </div>
            )}

            {submission?.remediation && !passed && (
              <div className="hint-box">
                <strong>Let&apos;s make it smaller.</strong>
                <p>{submission.remediation.simpler_explanation}</p>
                <p>
                  <em>Try this first:</em> {submission.remediation.smaller_subtask}
                </p>
              </div>
            )}
          </div>

          <div>
            <CodeEditor value={code} onChange={setCode} />
            <div className="run-row">
              <button onClick={onRun} disabled={running}>
                {running ? "Running…" : "▶ Run & Test"}
              </button>
              <button className="secondary" onClick={() => setCode(mission.starter_code)}>
                Reset code
              </button>
            </div>

            {error && <div className="error-banner">{error}</div>}

            {run && (run.output || run.error) && (
              <div className="console">
                {run.output}
                {run.error && <span style={{ color: "var(--bad)" }}>{run.error}</span>}
              </div>
            )}

            {run && run.results.length > 0 && (
              <ul className="test-list">
                {run.results.map((t, i) => (
                  <li key={i} className={t.passed ? "pass" : "fail"}>
                    {t.passed ? "✔" : "✘"} {t.description}
                    {t.error ? ` — ${t.error}` : ""}
                  </li>
                ))}
              </ul>
            )}

            {submission && (
              <div className={`feedback ${passed ? "success" : "failure"}`}>
                <p className="mentor-line" style={{ margin: 0 }}>
                  {mentor}: “{submission.story_feedback}”
                </p>
                <p style={{ marginBottom: 0 }}>{submission.technical_feedback}</p>
                {passed && (
                  <button style={{ marginTop: "0.9rem" }} onClick={onClose}>
                    {submission.next_action === "finish"
                      ? "Finish the story →"
                      : "Continue the journey →"}
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
