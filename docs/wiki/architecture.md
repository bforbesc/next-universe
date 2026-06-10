# Architecture

System structure, trust boundaries, and the seams that carry the platform
through the [stages](stages.md).

## Overview

```
┌────────────────────────────  Browser  ────────────────────────────┐
│  Next.js app                                                      │
│  ├── Profile form                                                 │
│  ├── Game engine (Phaser) — renders a *format* ("mission-map-2d") │
│  ├── Mission screen (Monaco editor, story panel, feedback)        │
│  └── Code runner: Pyodide in a Web Worker                         │
│       · browser sandbox = no host/filesystem/network access       │
│       · hard 20s timeout via worker termination                   │
└──────────────┬────────────────────────────────────────────────────┘
               │ JSON over HTTPS
┌──────────────▼────────────────────────────────────────────────────┐
│  FastAPI backend                                                  │
│  ├── /students /adventures /submissions /progress                 │
│  ├── Generator orchestration (LLM-first, template fallback)       │
│  │    ├── llm.py — Claude structured outputs (messages.parse)     │
│  │    ├── fallback.py — golden content (4 themes)                 │
│  │    └── code_verify.py — "test the tests" subprocess gate       │
│  ├── Curriculum loader — courses are data (curriculum/*.json)     │
│  └── SQLAlchemy: students, adventures (verbatim), submissions,    │
│      mission_states (attempts/completion → telemetry)             │
└───────────────────────────────────────────────────────────────────┘
```

## Core principle

**The LLM never generates game code at runtime.** It fills validated JSON
schemas (`backend/app/schemas.py`: `StoryArc`, `Mission`); a deterministic
engine consumes only validated instances. Correctness of student code is
decided by deterministic hidden tests, never by the LLM — the LLM writes
story, explanations, hints, remediation.

## Trust boundaries

| Input | Trust | Gate |
|---|---|---|
| LLM output | Untrusted | (a) must parse into Pydantic schemas, (b) its `reference_solution` must pass its own `hidden_tests` in an isolated subprocess (`python -I`, hard timeout). Failure ⇒ template fallback. |
| Student code | Untrusted | Runs only in Pyodide (WASM) in a Web Worker in the student's own browser; hard timeout via worker termination. Backend stores attempt + verdict only. |
| Curriculum files | Trusted (repo-owned) | Schema-shaped JSON; loader validates module ids. |

Known POC tradeoff: hidden tests ship to the client (devtools-visible). When
stakes appear (certificates, classrooms), add server-side re-verification of
passing submissions — `code_verify.verify_program` already implements the
identical assertion contract.

## Data flow (happy path)

1. `POST /api/students` — profile persisted (`students.profile` JSON).
2. `POST /api/adventures` — loads curriculum modules → `generator.create_adventure`
   → verify gate → adventure persisted **verbatim** (arc + missions incl.
   `reference_solution`) → `mission_states` rows created → response strips
   `reference_solution` via the `Mission` response model.
3. Browser runs student code + hidden tests in Pyodide; `POST /api/submissions`
   reports the verdict → backend records the attempt, updates state, returns
   narrative + technical feedback, escalating hint (attempt N ⇒ hint N), and
   remediation after 3 failures.
4. `GET /api/adventures/{id}/progress` — completed/available/locked per mission;
   first incomplete mission is the only available one.

## Extension seams (what makes later stages cheap)

1. **Courses are data** — `curriculum/<course_id>.json`; loader is course-keyed;
   `POST /api/adventures` takes `course_id`. New topic = new file.
2. **Game formats are identifiers** — `Adventure.format` (today always
   `mission-map-2d`). Frontend maps format → renderer component; backend maps
   format → content schema + generator. New game type = new schema + renderer;
   profile/verification/progress/telemetry layers don't change.
3. **One generator entry point** — `generator.create_adventure(profile, modules)
   -> (name, arc, missions)`. Today: LLM-first with template fallback. Later: a
   registry keyed by (course, format) with A/B-able strategies.

## Reproducibility & telemetry

- Adventures stored verbatim ⇒ every playthrough reproducible/auditable;
  prompts regression-testable against stored outputs.
- Every attempt stored with code, per-test results, errors
  (`submissions` table) ⇒ the dataset for hint/difficulty tuning and, later,
  adaptive difficulty models.

Related: [content-pipeline.md](content-pipeline.md), [backend.md](backend.md),
[frontend.md](frontend.md), [deployment-aws.md](deployment-aws.md).
