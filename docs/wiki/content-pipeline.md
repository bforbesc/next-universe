# Content Pipeline

How a baseline curriculum becomes verified, personalized, playable missions.

```
curriculum/<course>.json ──► generator.create_adventure(profile, modules)
                                   │
                     ┌─────────────┴─────────────┐
                     │ LLM path (if API key)     │ template path (always works)
                     │ llm.py: messages.parse    │ fallback.py: golden content
                     │ → StoryArc, then each     │ 4 themes × vertical slice
                     │   MissionWithSolution,    │
                     │   chained for continuity  │
                     └─────────────┬─────────────┘
                                   ▼
                  code_verify.verify_program  ← "test the tests" gate
                  (reference_solution must pass its own hidden_tests,
                   isolated subprocess, hard timeout; failure ⇒ fallback)
                                   ▼
                  persist verbatim in `adventures` (reproducible)
```

## Baseline curriculum (the input)

`curriculum/python_beginner.json` — modules with `module_id`, `order`,
`concept`, `title`, `learning_objectives`, `explanation`, `examples`,
`common_mistakes`, `exercise_patterns`, `difficulty`.

- **The AI never invents the course.** Prompts embed module content verbatim
  (pinned by `tests/test_generator.py::test_llm_prompts_embed_baseline_curriculum`).
- Real course content is pending import (owner will paste it); current
  vertical-slice modules are fully written, the rest are placeholders.
- New course = new file; loader (`services/curriculum.py`) maps
  `course_id` → `<course_id with - as _>.json`, caches, validates module ids.

## Schemas (the contract)

`backend/app/schemas.py`, mirrored in `frontend/lib/types.ts`:

- `StoryArc` — theme, title, protagonist, world, conflict, goal, mentor,
  `mission_arc[]`, final challenge.
- `Mission` — story context (previous_state / current_problem /
  why_this_matters / narrative_stakes), learning objective, concept
  explanation, starter code, task, `hidden_tests[]`, `hints[3..5]`,
  success/failure feedback (technical + story), remediation, next-mission rules.
- `MissionWithSolution(Mission)` — adds `reference_solution`; internal only,
  stripped from API responses by the `Mission` response model.

**Hidden-test contract:** each `assertion` is a Python *boolean expression*
evaluated in the namespace after the student's code runs (e.g.
`"oxygen_level == 100"`). Never prose, never statements. Same contract in the
backend verifier and the browser harness.

## Storytelling requirements (quality bar)

Encoded in `llm.py::STORYTELLING_RULES` and exemplified by `fallback.py`:
protagonist, world with rules, central conflict, rising stakes, mentor with a
voice, payoff — and the Python concept must be the **in-world mechanism**
(variables store vital resources; conditionals make survival decisions; loops
automate repetition). Narrative continuity is mechanical: mission N+1's
`story_context.previous_state` **equals** mission N's
`success_feedback.story_feedback` (pinned by
`tests/test_content.py::test_story_continuity_between_missions`).

## Learning-science design rules

Evidence-backed rules from the [learning research stream](../../research/learning/charter.md)
(latest report: [2026-06-09](../../research/learning/reports/2026-06-09-learning-science.md));
each cites its effect there:

- **Story progression is the reward.** No leaderboards/points/badges as primary
  motivation loops (gamification meta-analyses: those drive extrinsic, not
  intrinsic motivation). Competence/autonomy/relatedness (SDT) map to
  difficulty adaptation + progress map / theme choice / mentor character.
- **Testing is retrieval practice** — keep tests per mission; later missions
  should also exercise earlier concepts ("callback" pattern).
- **Struggle before help** (desirable difficulties): hints should be opt-in,
  escalation preserved; remediation after repeated failure implements
  "structured guidance after productive failure".
- **Scaffold novices with worked examples and (later) Parsons-style widgets** —
  the best-evidenced supports for beginner programmers.

## Generation paths

- **Template (`fallback.py`)** — deterministic golden content; theme chosen by
  `preferred_theme` > interest keyword match > `explorer`. Personalization:
  name woven into narrative, difficulty shifted by preference (gentle −1 /
  challenging +1, clamped 1–5). Doubles as the LLM's quality bar and few-shot
  reference.
- **LLM (`llm.py`)** — `client.messages.parse` with `output_format=StoryArc`,
  then one call per mission (`output_format=MissionWithSolution`) chained with
  the previous mission's success story for continuity. Engine owns identity
  fields (mission_id, module, theme) and overwrites them. Arc concepts must
  match the curriculum exactly or generation is rejected.
- **Orchestration (`generator.py`)** — LLM-first when `llm_available()`, any
  exception/validation/verification failure logs and falls back. Both paths
  pass the verify gate.

## Verification gate

`code_verify.verify_program(solution, tests, timeout=5)` runs the solution and
evaluates each assertion in `python -I -c` (no site-packages, no env) with a
hard timeout, via JSON over stdin. A mission whose reference solution cannot
pass its own tests is **rejected before persistence** — a correct student must
never fail because of broken generated tests.

## Changing this pipeline — checklist

- Schema change → update `schemas.py` + `frontend/lib/types.ts` + prompts in
  `llm.py` + golden content in `fallback.py` + tests.
- New theme → add a `THEMES` entry in `fallback.py` (keywords, arc, missions);
  `tests/test_content.py` parametrizes over all themes automatically.
- New module content → extend the theme packs or rely on the LLM path;
  template generator raises on modules it has no content for.
- Prompt change → keep the curriculum-embedding tests green; eval against
  stored adventures before shipping.
