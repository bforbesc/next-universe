# Next Universe — AI-Personalized Learning Game Platform (POC)

A proof of concept for a platform where students learn by playing AI-personalized,
story-driven games. This POC teaches **beginner Python**: a student enters their
profile and interests, the system transforms a **baseline curriculum** into a
personalized story world with coding missions, and a deterministic 2D game engine
renders it.

**Core loop:** student profile → baseline curriculum → story world → mission →
coding challenge → deterministic tests → hints/remediation → next mission.

## Architecture in one paragraph

The LLM never generates game code. It fills **validated JSON schemas**
(`StoryArc`, `Mission`) that a deterministic engine consumes. Correctness of
student code is decided by **deterministic hidden tests** executed in a
sandboxed Pyodide Web Worker in the browser (hard 20s timeout); the LLM only
writes the content — story, explanations, hints, remediation. Every generated
mission ships with a reference solution that is executed against its own hidden
tests server-side **before** it is persisted ("test the tests"); content that
fails verification is rejected and the system falls back to hand-written
golden content, so the product works end-to-end with no API key at all.

```
frontend/  Next.js + Phaser (2D map) + Monaco (editor) + Pyodide (code runner)
backend/   FastAPI + SQLAlchemy; generation, verification, progress, telemetry
curriculum/  Baseline course content (data, not code) — one JSON per course
docs/      Architecture: AWS deployment + platform evolution plan
```

## Running locally

Backend (Python 3.11+):

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend (Node 20+):

```bash
cd frontend
npm install
npm run dev      # http://localhost:3000
```

Without `ANTHROPIC_API_KEY` the backend uses the built-in golden content
(themes: space, football, music, explorer). With a key it generates fully
personalized content with Claude:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export ANTHROPIC_MODEL=claude-opus-4-8   # default
```

Other env vars: `DATABASE_URL` (default: local SQLite; Postgres-ready),
`CURRICULUM_DIR`, `CORS_ORIGINS`.

## Tests (the project is built TDD)

```bash
cd backend && python3 -m pytest        # 44 tests: API flows, generation, verification
cd frontend && npm test                # harness verified against real CPython
```

What the tests pin down:

- **API flows**: profile → adventure → escalating hints → remediation → progress → finish.
- **Content quality bars**: every theme validates against the schemas, story
  continuity chains between missions, personalization reaches the narrative,
  difficulty preference shifts mission difficulty.
- **Test-the-tests**: every mission's reference solution must pass its own
  hidden tests in an isolated subprocess, or the content is rejected.
- **Generator resilience**: LLM unavailable/failing/producing broken tests ⇒
  graceful fallback, never a broken game.
- **Runner semantics**: the browser harness is executed with real CPython in CI
  to guarantee it matches the backend verifier's contract.

## Replacing the placeholder curriculum with the real course

`curriculum/python_beginner.json` is the baseline the AI personalizes — it is
**data, not code**. Each module has: `concept`, `learning_objectives`,
`explanation`, `examples`, `common_mistakes`, `exercise_patterns`, `difficulty`.
Replace the placeholder text with the real course content module-by-module;
the generator prompts embed it verbatim. Adding a new course = adding a new
`curriculum/<course_id>.json` and POSTing `{"course_id": "<course-id>"}`.

## API

| Endpoint | Purpose |
|---|---|
| `POST /api/students` | create a student profile |
| `POST /api/adventures` | generate + persist a personalized adventure (arc + missions) |
| `GET /api/adventures/{id}` | fetch a stored adventure (reproducible) |
| `GET /api/adventures/{id}/progress` | mission unlock states + attempt counts |
| `POST /api/submissions` | record an attempt; returns narrative + technical feedback, escalating hints, remediation |

## Where the platform goes next

See `docs/architecture.md` for the AWS deployment mapping and the extension
points designed in today: format-keyed generators and renderers (new game
types), course-keyed curricula (new subjects), and the path from
"LLM fills schemas" to "LLM designs formats" as models improve.
