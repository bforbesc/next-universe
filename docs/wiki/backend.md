# Backend

FastAPI service in `backend/`. Python 3.11+, Pydantic v2, SQLAlchemy 2.0.

## Run

```bash
cd backend
pip install -r requirements.txt
python3 -m pytest                          # must stay green
uvicorn app.main:app --reload --port 8000
```

Env: `DATABASE_URL` (default local SQLite; Postgres-ready), `ANTHROPIC_API_KEY`
(optional — enables LLM generation), `ANTHROPIC_MODEL` (default
`claude-opus-4-8`), `CURRICULUM_DIR`, `CORS_ORIGINS`.

## Endpoints (all under `/api`)

| Endpoint | Behavior |
|---|---|
| `POST /students` → 201 | persist profile (`StudentProfileIn`), returns id |
| `GET /students/{id}` | profile or 404 |
| `POST /adventures` → 201 | `{student_id, course_id?, concepts?}` → generate (LLM or template) → verify → persist verbatim → create `mission_states` → return `AdventureOut` (no `reference_solution`) |
| `GET /adventures/{id}` | stored adventure, reproducible |
| `GET /adventures/{id}/progress` | per-mission `completed/available/locked` + attempts; only the first incomplete mission is `available` |
| `POST /submissions` | record attempt; passed ⇒ `next`/`finish` + success feedback; failed ⇒ `retry` with hint #min(attempts, len(hints)), or `remediate` (+ remediation payload) from the 3rd failure |
| `GET /health` | liveness |

The browser decides pass/fail (Pyodide runs the hidden tests) and reports it;
the backend records and coaches. Server-side re-verification is a planned
hardening step ([architecture.md](architecture.md) §trust boundaries).

## Data model (`app/models.py`)

| Table | Purpose |
|---|---|
| `students` | name + full profile JSON |
| `adventures` | generator name, `format`, story_arc JSON, missions JSON (incl. `reference_solution` — audit only) |
| `submissions` | every attempt: code, passed, per-test results, error — telemetry |
| `mission_states` | per (adventure, mission): attempts, completed — drives progress/hints |

Tables are created on startup (`Base.metadata.create_all`). Move to Alembic
migrations before the first shared deployment.

## Services

See [content-pipeline.md](content-pipeline.md) for `curriculum.py`,
`generator.py`, `llm.py`, `fallback.py`, `code_verify.py`.

## Gotchas

- `generator.py` re-exports `llm_available` / `generate_llm_adventure` so tests
  monkeypatch `app.services.generator.<name>` — keep those names stable.
- `Mission` (response model) silently drops extra keys — that is the mechanism
  that strips `reference_solution`; don't "fix" it.
- Hint indexing is 1-based for display: attempt N shows `hints[N-1]`, clamped
  to the last hint.
- `REMEDIATION_THRESHOLD = 3` in `routers/submissions.py`.
