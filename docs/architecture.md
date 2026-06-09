# Architecture — POC today, platform tomorrow

## 1. System overview

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

### Trust boundaries

- **LLM output is untrusted** until (a) it parses into the Pydantic schemas and
  (b) its reference solution passes its own hidden tests in an isolated
  subprocess (`python -I`, hard timeout). Failures fall back to golden content.
- **Student code is untrusted** and never touches the backend interpreter: it
  runs in Pyodide (WASM) inside a Web Worker in the student's own browser.
  The backend only stores the attempt and the verdict.
- POC tradeoff: hidden tests are visible to a motivated student via devtools.
  Acceptable now; when stakes appear, add server-side re-verification of
  passing submissions (the verifier already exists — same assertion contract).

## 2. AWS deployment mapping (when we deploy)

| Component | AWS service | Notes |
|---|---|---|
| Frontend | S3 + CloudFront | static export / SSG; Pyodide from CDN |
| Backend API | ECS Fargate (or Lambda + API GW) | stateless, 12-factor; container already trivial |
| Database | RDS PostgreSQL | swap `DATABASE_URL`; SQLAlchemy is dialect-agnostic |
| LLM | Anthropic API or Claude on AWS | model id via `ANTHROPIC_MODEL` |
| Generation queue | SQS + worker (later) | adventure generation is the only slow call; make `POST /adventures` async when LLM latency matters |
| Course assets | S3 | `CURRICULUM_DIR` → S3 sync or DB table |
| Telemetry | CloudWatch + the `submissions` table | failure patterns per concept already captured |
| Auth | Cognito (later) | the POC is anonymous-profile based on purpose |
| Secrets | Secrets Manager / SSM | `ANTHROPIC_API_KEY` |

Nothing in the code changes for this mapping — only configuration.

## 3. Built-in extension points (the platform jump)

The long-term product is "generate any game for any topic". Today's code keeps
that door open in three specific places:

1. **Courses are data.** A course is `curriculum/<course_id>.json` with modules
   (objectives, explanation, examples, mistakes, exercise patterns). New topic
   = new file. The generator prompts embed the module content verbatim — the
   AI transforms the course, it never invents it.

2. **Game formats are identifiers, not assumptions.** Every adventure carries
   `format` (today: `"mission-map-2d"`). The frontend maps format → renderer
   component; the backend maps format → content schema + generator. A new game
   type (dialogue-driven, puzzle-grid, resource-sim) is a new schema + a new
   renderer — the profile, curriculum, verification, progress and telemetry
   layers are format-agnostic and unchanged.

3. **Generators are swappable behind one function.**
   `generator.create_adventure(profile, modules) -> (name, arc, missions)` is
   the single seam. Today it tries Claude and falls back to templates. Tomorrow
   it becomes a registry keyed by (course, format) with A/B-able strategies.

### As models improve — the capability ladder

| Stage | LLM responsibility | Engine responsibility | Gate |
|---|---|---|---|
| **Now (POC)** | Fill StoryArc/Mission schemas; hints; remediation | Fixed format, fixed mechanics | Schema validation + test-the-tests |
| Next | Choose mechanics per mission from a widget library (drag-blocks, fill-in, free code); generate per-student difficulty variants | Render widget compositions | Same gates + pedagogy evals on stored content |
| Later | Design new *formats* (schema + rules) offline, reviewed before activation | Interpret declarative format definitions | Human review + automated playtests |
| Eventually | Generate game logic in a constrained DSL at runtime | Execute sandboxed DSL | Static analysis + simulation before serving |

The invariant at every stage: **generated content is validated, verified and
persisted before a student sees it** — capability grows, the safety contract
doesn't change.

## 4. Reproducibility & telemetry

- Adventures are stored verbatim (arc + missions + reference solutions): every
  playthrough is reproducible and auditable; prompts can be regression-tested
  against stored outputs.
- Every attempt is stored with code, per-test results and errors —
  the dataset for "which concept/story/hint combinations work" and, later, for
  the adaptive difficulty model.
