# Getting Started (technical)

Setup, run, test, and configuration. For what the project *is*, read the
[root README](../../README.md); for how it's built, start at
[architecture.md](architecture.md).

## Prerequisites

- Python 3.11+ (backend, and required by frontend harness tests)
- Node 20+ (frontend)

## Backend

```bash
cd backend
pip install -r requirements.txt
python3 -m pytest                          # full suite — must stay green
uvicorn app.main:app --reload --port 8000
```

## Frontend

```bash
cd frontend
npm install
npm test         # vitest (harness tests execute real CPython)
npm run dev      # http://localhost:3000 (expects backend on :8000)
npm run build    # type-check + production build
```

## Environment variables

| Var | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | unset | enables LLM generation; without it the template (golden content) generator covers the full loop |
| `ANTHROPIC_MODEL` | `claude-opus-4-8` | generation model |
| `DATABASE_URL` | local SQLite file | any SQLAlchemy DSN (Postgres-ready) |
| `CURRICULUM_DIR` | `curriculum/` | baseline course content location |
| `CORS_ORIGINS` | `http://localhost:3000` | comma-separated allowed origins |
| `NEXT_PUBLIC_API_URL` (frontend) | `http://localhost:8000` | backend base URL |

## API quick reference

| Endpoint | Purpose |
|---|---|
| `POST /api/students` | create a student profile |
| `POST /api/adventures` | generate + persist a personalized adventure (`{student_id, course_id?, concepts?}`) |
| `GET /api/adventures/{id}` | fetch a stored adventure (reproducible) |
| `GET /api/adventures/{id}/progress` | mission unlock states + attempt counts |
| `POST /api/submissions` | record an attempt; returns feedback, hints, remediation |
| `GET /api/health` | liveness |

Full behavior: [backend.md](backend.md).

## Replacing the placeholder curriculum

`curriculum/python_beginner.json` is the baseline the AI personalizes — data,
not code. Each module needs: `concept`, `learning_objectives`, `explanation`,
`examples`, `common_mistakes`, `exercise_patterns`, `difficulty`. Replace the
placeholder text module-by-module; the generator embeds it verbatim
([content-pipeline.md](content-pipeline.md)). Adding a course = adding
`curriculum/<course_id>.json` (dashes in the id become underscores in the
filename) and passing `course_id` to `POST /api/adventures`.
