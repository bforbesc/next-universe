# Stages — Product Roadmap

**We build for where the models are going, not where they are.** Each stage
raises the LLM's responsibility; the safety contract never changes:
*generated content is schema-validated, test-verified and persisted before a
student sees it*. Architecture decisions today must not block later stages —
when a request belongs to a later stage, build the seam, not the feature.

## Stage overview

| Stage | Name | Content | Topics | Game formats | Status |
|---|---|---|---|---|---|
| **1** | Single game, predetermined content | Hand-written (template/golden) | Beginner Python only | `mission-map-2d` only | **← current** |
| **2** | More games, predetermined content | Hand-written | Multiple (new curricula) | A few, still hand-built | future |
| **3** | Predetermined topics, personalized content | LLM-generated within fixed schemas/formats | Curated catalog | Fixed library | machinery exists, gated |
| **4** | Fully auto-generated games | LLM designs mechanics/formats | Any topic | Generated within a constrained engine/DSL | future |

Cross-cutting at every stage: the **[game-stack track](game-stack.md)** —
graphics, dynamics and game feel improve continuously (richer 2D now, 3D when
justified) without changing the content pipeline.

## Stage 1 — single game, predetermined content (current)

One game (`mission-map-2d`), one topic (beginner Python), deterministic
hand-written content (`backend/app/services/fallback.py`: space, football,
music, explorer themes). Personalization at this stage = theme matching +
name weaving + difficulty shift, all deterministic.

**Done** (vertical slice, all tested):
- Full learning loop: profile → adventure → 2D map → missions → in-browser
  code execution → deterministic tests → escalating hints → remediation →
  progress → finale.
- Golden content for the vertical slice (variables, conditionals, loops) × 4 themes.
- Verification gate ("test the tests"), reproducible stored adventures,
  attempt telemetry.

**Left in Stage 1:**
- [ ] Import the real Python course into `curriculum/python_beginner.json`
      (owner has the content; placeholder structure is ready).
- [ ] Extend content beyond the 3-module slice toward the 10-module course
      (hand-written per theme, or via the Stage-3 generator as an authoring
      tool whose output is reviewed and frozen — preferred).
- [ ] Playtest pass with 2–3 real students; tune hints/difficulty from the
      `submissions` telemetry.
- [ ] First AWS deployment ([deployment-aws.md](deployment-aws.md)).

**Exit criteria:** a student can play 5–10 missions of the real curriculum end
to end, deployed, with a coherent story arc.

## Stage 2 — more games, predetermined content, more topics

New topics (e.g. web basics, math, another language) and possibly 1–2 new game
formats, still with hand-authored/frozen content.

What the codebase already provides:
- New topic = new `curriculum/<course_id>.json` + content pack. Zero engine changes
  (`backend/app/services/curriculum.py` is course-keyed; `POST /api/adventures`
  takes `course_id`).
- New game format = new `format` id + frontend renderer + (if needed) new
  content schema. Profile, verification, progress, telemetry layers are
  format-agnostic ([architecture.md](architecture.md) §seams).

Work items when Stage 2 starts: format registry on both sides (today the
mapping is implicit because there is one format), an authoring/review workflow
for frozen content, course catalog UI.

## Stage 3 — predetermined topics, personalized content

The LLM generates the story arc and missions per student, inside the fixed
schemas and format library. Topics remain a curated catalog.

**Forward investment already built** (because we build for where models are
going): `backend/app/services/llm.py` + `generator.py` implement exactly this —
Claude structured outputs filling `StoryArc`/`Mission`, schema validation,
test-the-tests gate, graceful fallback. It activates with `ANTHROPIC_API_KEY`.

Work items to call Stage 3 "live": prompt evals against stored golden content,
pedagogy review loop, per-student difficulty adaptation from telemetry
(`submissions`/`mission_states` tables already capture the signal), cost/latency
budget (generation is upfront-per-adventure by design; consider SQS async),
content moderation/age-appropriateness checks.

## Stage 4 — fully auto-generated games

The LLM designs game mechanics and formats, not just content. Capability
ladder (each step keeps the same gates, plus new ones):

1. LLM **composes** mechanics per mission from a widget library (drag-blocks,
   fill-in, free code) → engine renders compositions.
2. LLM **designs formats offline** (schema + rules), human-reviewed and
   playtested before activation → engine interprets declarative format definitions.
3. LLM **generates game logic in a constrained DSL** at serve time → static
   analysis + simulated playthroughs before a student sees it.

Stage 4 is intentionally unbuilt. The only Stage-4 obligations today are the
seams: `format` as data, one generator entry point
(`generator.create_adventure`), schemas as the only LLM↔engine boundary.

## Decision log

| Decision | Stage rationale |
|---|---|
| Generate full adventure upfront, not per-mission at runtime | Story coherence + reproducibility; revisit only if Stage 3 personalization needs mid-game adaptation beyond hints |
| Pyodide in-browser execution | Removes sandbox infra through at least Stage 3; server-side re-verification planned when stakes appear |
| Hidden tests visible to client | POC tradeoff, acceptable until certificates/classrooms |
| Phaser 2D, no Unity | Stage 1–3 risk is content quality, not graphics; see [game-stack.md](game-stack.md) for the 3D path |
