import type {
  Adventure,
  Progress,
  RunResult,
  StudentProfileIn,
  SubmissionResult,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!resp.ok) {
    const body = await resp.text().catch(() => "");
    throw new Error(`${resp.status} ${resp.statusText}: ${body}`);
  }
  return resp.json();
}

export function createStudent(profile: StudentProfileIn): Promise<{ id: number }> {
  return request("/api/students", { method: "POST", body: JSON.stringify(profile) });
}

export function createAdventure(studentId: number): Promise<Adventure> {
  return request("/api/adventures", {
    method: "POST",
    body: JSON.stringify({ student_id: studentId }),
  });
}

export function getAdventure(adventureId: number): Promise<Adventure> {
  return request(`/api/adventures/${adventureId}`);
}

export function getProgress(adventureId: number): Promise<Progress> {
  return request(`/api/adventures/${adventureId}/progress`);
}

export function submitAttempt(
  adventureId: number,
  missionId: string,
  code: string,
  run: RunResult,
): Promise<SubmissionResult> {
  return request("/api/submissions", {
    method: "POST",
    body: JSON.stringify({
      adventure_id: adventureId,
      mission_id: missionId,
      code,
      passed: run.passed,
      test_results: run.results,
      error: run.error,
    }),
  });
}
