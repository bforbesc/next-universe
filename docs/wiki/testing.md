# Testing

The project is built TDD: **write the failing test first**, then the
implementation. Every behavior change lands with tests. The test suites are
the spec — read them before changing behavior.

## Run

```bash
cd backend && python3 -m pytest          # 44 tests
cd frontend && npm test                  # vitest; requires python3 on PATH
```

Backend tests use a throwaway SQLite file and run with no API key
(`tests/conftest.py` clears `ANTHROPIC_API_KEY` before app import).

## What each suite pins down

| Suite | Pins |
|---|---|
| `backend/tests/test_api.py` | End-to-end flows: profile CRUD/validation; adventure generation (arc/missions/order, `reference_solution` never leaks); progress unlocking (`available/locked/completed`); failure ⇒ hint 1→2→3 ⇒ remediation; success ⇒ next/finish; attempts persisted |
| `backend/tests/test_content.py` | Golden-content quality bars, parametrized over **all** themes: schema validity, reference solutions pass own tests, arc↔missions↔curriculum order, story continuity chain (`previous_state == previous mission's success story`), interest→theme matching + fallback, personalization reaches narrative, difficulty preference shifts difficulty, hints 3–5 + remediation present |
| `backend/tests/test_generator.py` | Orchestration: no key ⇒ template; LLM exception ⇒ fallback; LLM content failing verification ⇒ fallback; verified LLM content used; prompts embed baseline curriculum verbatim |
| `backend/tests/test_verifier.py` | `verify_program`: pass, fail-with-description, crash, missing names, infinite-loop timeout |
| `backend/tests/test_curriculum.py` | Course loading, module ordering, content presence, unknown module/course errors |
| `frontend/lib/harness.test.ts` | Browser harness executed with **real CPython**: pass/fail/stdout capture/crash/syntax error; hostile code (quotes, backslashes, unicode) can't break the embedding; sys tampering can't fake a pass; empty test list ≠ pass |

## Conventions

- New theme or schema field ⇒ the parametrized content tests cover it
  automatically or fail loudly — extend `test_content.py` when adding quality bars.
- LLM tests never call the network: monkeypatch
  `app.services.generator.{llm_available, generate_llm_adventure}`.
- The harness test doubles as the contract test between
  `frontend/lib/harness.ts` and `backend/app/services/code_verify.py` — if you
  change one side's semantics, both suites must be updated in the same change.
- Keep suites fast (<10s backend) — they run on every change.

## Known gaps (acceptable for Stage 1, revisit later)

- No component/E2E tests for the React/Phaser UI (manual playtest covers it).
- No live LLM integration test (would need a key + budget; prompt evals are a
  Stage-3 work item — see [stages.md](stages.md)).
