/**
 * Runs student code in Pyodide inside a Web Worker:
 * - the browser sandbox isolates the code (no host filesystem / backend access)
 * - the worker keeps the UI responsive
 * - a hard timeout terminates runaway code (infinite loops) by killing the
 *   worker — the only reliable way to stop synchronous Python in the browser.
 */
import { buildHarnessProgram, type HiddenTest } from "./harness";
import type { RunResult } from "./types";

const TIMEOUT_MS = 20_000;

let worker: Worker | null = null;
let nextId = 0;

function getWorker(): Worker {
  if (!worker) {
    worker = new Worker("/pyodide-worker.js");
  }
  return worker;
}

/** Optionally call early (e.g. when a mission opens) to hide the ~3s Pyodide
 * cold start behind reading time. */
export function warmUp(): void {
  getWorker();
}

export function runPython(code: string, tests: HiddenTest[]): Promise<RunResult> {
  const program = buildHarnessProgram(code, tests);
  const id = ++nextId;
  const w = getWorker();

  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      w.removeEventListener("message", onMessage);
      // Terminating is the only way to stop a stuck synchronous loop.
      w.terminate();
      worker = null;
      resolve({
        output: "",
        error:
          "Your code ran for more than 20 seconds and was stopped. " +
          "Check for a loop that never ends (does its condition ever become False?).",
        passed: false,
        results: [],
      });
    }, TIMEOUT_MS);

    function onMessage(event: MessageEvent) {
      const data = event.data as
        | { id: number; ok: true; resultJson: string }
        | { id: number; ok: false; error: string };
      if (data.id !== id) return;
      clearTimeout(timer);
      w.removeEventListener("message", onMessage);
      if (data.ok) {
        resolve(JSON.parse(data.resultJson) as RunResult);
      } else {
        resolve({ output: "", error: data.error, passed: false, results: [] });
      }
    }

    w.addEventListener("message", onMessage);
    w.postMessage({ id, program });
  });
}
