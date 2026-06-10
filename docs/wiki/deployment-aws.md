# Deployment — AWS

The code is 12-factor; deployment is configuration, not code change. Nothing
here blocks local development — deploy when Stage 1 exit criteria approach
([stages.md](stages.md)).

## Service mapping

| Component | AWS service | Notes |
|---|---|---|
| Frontend | S3 + CloudFront | `next build` static assets; Pyodide + Monaco load from public CDNs |
| Backend API | ECS Fargate (or Lambda + API Gateway) | stateless; containerize `uvicorn app.main:app` |
| Database | RDS PostgreSQL | set `DATABASE_URL`; SQLAlchemy is dialect-agnostic; add Alembic before first shared deploy |
| LLM | Anthropic API (or Claude on AWS) | `ANTHROPIC_API_KEY` from Secrets Manager; model via `ANTHROPIC_MODEL` |
| Generation queue | SQS + worker (later) | `POST /adventures` is the only slow call (LLM path); make async when latency matters, return 202 + poll |
| Course content | S3 (or DB table) | `CURRICULUM_DIR` currently reads local files |
| Telemetry | CloudWatch logs + `submissions` table | failure patterns per concept already captured |
| Auth | Cognito (later) | POC is anonymous-profile by design |

## Environment variables

| Var | Default | Deploy value |
|---|---|---|
| `DATABASE_URL` | local SQLite | RDS Postgres DSN |
| `ANTHROPIC_API_KEY` | unset (template mode) | Secrets Manager |
| `ANTHROPIC_MODEL` | `claude-opus-4-8` | as needed |
| `CURRICULUM_DIR` | `curriculum/` in repo | baked into image or S3 sync |
| `CORS_ORIGINS` | `http://localhost:3000` | CloudFront domain |
| `NEXT_PUBLIC_API_URL` (frontend) | `http://localhost:8000` | API domain |

## Pre-deploy checklist

- [ ] Alembic migrations replace `create_all` on startup.
- [ ] Healthcheck wired to `/api/health` (exists).
- [ ] Rate limiting on `POST /adventures` (LLM cost control).
- [ ] Postgres run of the backend test suite (`DATABASE_URL` against a local
      Postgres) — JSON columns are the main thing to verify.
- [ ] IAM: task role limited to Secrets Manager read + RDS connect; no broad S3.
- [ ] CloudWatch alarm on generation fallback rate (`generator` column —
      a spike means the LLM path is failing).

## Security notes

- Student code never executes on AWS — it runs in the student's browser
  (Pyodide). The backend only stores attempts.
- LLM content is verified server-side before persistence
  ([content-pipeline.md](content-pipeline.md) §verification gate); the
  verification subprocess (`python -I`, timeout) is the only place generated
  code executes — keep it off the request path if it ever becomes a bottleneck
  (move generation to the SQS worker).
- **Verifier sandboxing.** The verification subprocess runs LLM-generated code,
  so it is treated as untrusted: it runs with a **scrubbed environment** (no
  backend secrets — `code_verify.py` passes only `PATH`) and assertions are
  evaluated with restricted builtins. When the LLM generation path is enabled
  in production, additionally run it with **no network egress and minimal
  syscall/filesystem access** (a locked-down container, gVisor/seccomp, or a
  dedicated low-privilege worker) so that a prompt-injection-induced malicious
  reference solution cannot reach the network or the host. The default
  template path executes only trusted, hand-written code.
