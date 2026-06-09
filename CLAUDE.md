# CLAUDE.md

AI-personalized educational game platform. Students learn by playing story-driven
games; an LLM transforms a baseline curriculum into personalized missions that a
deterministic game engine renders. Current scope: beginner Python. Long-term:
any game for any topic (see `docs/wiki/stages.md` — we are in Stage 1).

## Docs for agents

`docs/wiki/` is the LLM wiki — one topic per page, read what the task touches:

| Page | Read when |
|---|---|
| `docs/wiki/stages.md` | any roadmap/scope question; deciding if a feature belongs now |
| `docs/wiki/architecture.md` | changing system structure, trust boundaries, data flow |
| `docs/wiki/content-pipeline.md` | touching curriculum, generation, prompts, verification |
| `docs/wiki/backend.md` | touching `backend/` |
| `docs/wiki/frontend.md` | touching `frontend/` |
| `docs/wiki/game-stack.md` | game feel, graphics, renderer, 3D considerations |
| `docs/wiki/testing.md` | writing or running tests |
| `docs/wiki/deployment-aws.md` | deployment, infra, env config |

## Commands

```bash
# backend (Python 3.11+, from backend/)
pip install -r requirements.txt
python3 -m pytest                      # full suite — must stay green
uvicorn app.main:app --reload --port 8000

# frontend (Node 20+, from frontend/)
npm install
npm test                               # vitest (runs real CPython for harness tests)
npm run build                          # type-check + production build
npm run dev                            # http://localhost:3000
```

No `ANTHROPIC_API_KEY` needed: the template generator covers the full loop.

## Hard rules (do not violate)

1. **TDD.** Write the failing test first, then the implementation. Every behavior
   change lands with tests.
2. **The LLM never generates game code at runtime.** It fills the Pydantic
   schemas in `backend/app/schemas.py`. The engine only consumes validated
   instances.
3. **No generated mission is persisted unverified.** Its `reference_solution`
   must pass its own `hidden_tests` via `code_verify.verify_program` first.
4. **Correctness comes from deterministic tests, never from the LLM.** The LLM
   writes story, explanations, hints — not verdicts.
5. **The product must work with no API key.** Never make the template fallback
   path depend on the LLM path.
6. **`reference_solution` never reaches the client.** It is stored in the DB
   (audit) and stripped by the `Mission` response model.
7. **Schema sync.** `backend/app/schemas.py` and `frontend/lib/types.ts` are
   mirrors — change both or neither. The Pyodide harness
   (`frontend/lib/harness.ts`) and backend verifier
   (`backend/app/services/code_verify.py`) share one contract: assertions are
   Python boolean expressions evaluated in the student-code namespace.
8. **Student code runs only in the browser sandbox** (Pyodide Web Worker, hard
   timeout) — never in the backend interpreter.
9. **Courses and content are data, not code.** New topic = new
   `curriculum/<course_id>.json`. New game type = new `format` id + renderer +
   schema, not edits to format-agnostic layers.

## Repo map

```
curriculum/            baseline course content (JSON; the AI personalizes THIS)
backend/app/
  schemas.py           the contract — StoryArc, Mission, submissions, progress
  models.py            SQLAlchemy: students, adventures, submissions, mission_states
  routers/             students, adventures (+progress), submissions
  services/
    curriculum.py      course loader (course_id-keyed)
    generator.py       orchestration seam: LLM-first, template fallback, verify gate
    llm.py             Claude structured outputs (messages.parse) + prompts
    fallback.py        golden content: 4 themes x vertical slice; few-shot quality bar
    code_verify.py     "test the tests" subprocess gate
backend/tests/         the spec — read these to understand intended behavior
frontend/
  app/                 profile form (/), game page (/play/[id])
  components/          GameCanvas (Phaser map), MissionPanel, CodeEditor, StoryIntro
  lib/                 api client, types (schema mirror), harness, pyodideRunner
  public/pyodide-worker.js   sandboxed Python runner
docs/wiki/             the LLM wiki (start at stages.md)
```

## Conventions

- Pydantic v2 (`model_dump`, `model_validate`), SQLAlchemy 2.0 typed mappings.
- Next.js App Router; anything touching `window`/Phaser is a client component,
  Phaser is `dynamic(..., { ssr: false })`.
- Anthropic model id via `ANTHROPIC_MODEL` env (default `claude-opus-4-8`);
  structured outputs via `client.messages.parse(..., output_format=Model)`.
- Mission ids: `m<N>-<module_id>` (e.g. `m2-conditionals`) — the engine owns
  identity fields, generated content gets them overwritten.
