# Frontend

Next.js (App Router, TypeScript) in `frontend/`. Node 20+.

## Run

```bash
cd frontend
npm install
npm test          # vitest; harness tests execute real CPython (python3 required)
npm run dev       # http://localhost:3000 (expects backend on :8000)
npm run build     # type-check + production build
```

Env: `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).

## Structure

| Path | Role |
|---|---|
| `app/page.tsx` | profile form → `POST /students` → `POST /adventures` → redirect `/play/[id]` |
| `app/play/[id]/page.tsx` | loads adventure + progress; story intro → map → mission panel → finale |
| `components/GameCanvas.tsx` | Phaser renderer for the `mission-map-2d` format: themed map, arrow-key player, SPACE/click to enter unlocked nodes; remounts when progress changes |
| `components/MissionPanel.tsx` | story context → explanation (mentor-voiced) → task → editor → run → feedback; hints are **opt-in** (button, reveal resets per attempt — desirable-difficulties rule in [content-pipeline.md](content-pipeline.md)); remediation after repeated failure |
| `components/CodeEditor.tsx` | Monaco (`@monaco-editor/react`), Python, dark |
| `components/StoryIntro.tsx` | arc presentation overlay |
| `lib/types.ts` | **mirror of `backend/app/schemas.py`** — keep in sync |
| `lib/api.ts` | typed fetch client |
| `lib/harness.ts` | builds the Python program (student code + hidden tests) Pyodide runs; JSON-literal embedding makes hostile code safe |
| `lib/pyodideRunner.ts` | worker lifecycle + 20s hard timeout (terminates and recreates the worker — only reliable way to stop synchronous Python) |
| `public/pyodide-worker.js` | loads Pyodide from CDN, runs harness programs |

## Code execution model

Student code never leaves the browser unexecuted territory: harness program
(see [content-pipeline.md](content-pipeline.md) §hidden-test contract) runs in
Pyodide (WASM) inside a Web Worker. Result: `{output, error, passed, results[]}`.
The verdict is then reported to `POST /api/submissions` for recording + coaching.
`warmUp()` is called when a mission opens so the ~3s Pyodide cold start hides
behind reading time. An empty test list never counts as a pass.

## SSR rules

- Phaser touches `window` ⇒ `GameCanvas` is imported with
  `dynamic(..., { ssr: false })` and all game UI is client components.
- Monaco loads client-side via `@monaco-editor/react`.

## Adding a renderer for a new game format (Stage 2+)

1. Add the format's content types to `lib/types.ts` (mirroring the backend schema).
2. Build a renderer component; key it off `adventure.format` in
   `app/play/[id]/page.tsx` (today the mapping is implicit — one format).
3. Reuse `MissionPanel`/runner if the format keeps code challenges; see
   [game-stack.md](game-stack.md) before choosing new tech.
