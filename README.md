# Next Universe

**Learning that plays like a game — built by AI, grounded in evidence.**

Next Universe is a platform where students learn by playing story-driven
games made for *them*. A student tells us who they are — age, interests, what
they already know — and the system turns a real course into a personal
adventure: a world built around what they love, a mentor with a voice, rising
stakes, and challenges where the thing being learned is the thing that saves
the day. A football fan learns Python by rescuing a club from relegation; a
space kid learns it by bringing a wounded starship home.

This is not a quiz with decorations. The concept *is* the game mechanic:
variables store the ship's oxygen, conditionals route its power, loops scan
the asteroid field. Story progress is the reward — because the research says
that's what makes learning stick.

## The ambition

Today: one course (beginner Python), one game world per student. Tomorrow:
**any game for any topic**. As AI models improve, the platform climbs a
staged ladder — from hand-crafted content, to AI-personalized stories within
fixed game formats, to fully generated games — while one safety contract
never changes: every piece of AI-generated content is validated and verified
before a student ever sees it, and whether a student's code is *correct* is
always decided by deterministic tests, never by an AI's opinion.

The roadmap: [Stage 1](docs/wiki/stages.md) (single game, predetermined
content — **current**) → Stage 2 (more games, more topics) → Stage 3
(AI-personalized content, machinery already built) → Stage 4 (fully
auto-generated games).

## How it works, in one breath

Student profile + baseline curriculum → AI writes a story world and missions
into strict, validated schemas → a deterministic game engine renders them →
the student writes real Python in the browser (sandboxed, instantly tested) →
the story reacts: success advances the plot, struggle earns hints, repeated
struggle earns a gentler path. Everything is designed against learning
science — retrieval practice, productive struggle, intrinsic motivation —
not gamification folklore.

## Try it

```bash
# backend            # frontend (new terminal)
cd backend           cd frontend
pip install -r requirements.txt && uvicorn app.main:app --port 8000
                     npm install && npm run dev   # → http://localhost:3000
```

Works fully offline from AI providers — without an API key you get the
built-in story worlds (space, football, music, exploration). Full setup,
tests and configuration: [Getting Started](docs/wiki/getting-started.md).

## Find your way around

| You want to… | Go to |
|---|---|
| Understand the roadmap and current stage | [docs/wiki/stages.md](docs/wiki/stages.md) |
| Set up, run, test, configure | [docs/wiki/getting-started.md](docs/wiki/getting-started.md) |
| Understand the system design & trust boundaries | [docs/wiki/architecture.md](docs/wiki/architecture.md) |
| See how AI turns a course into a game | [docs/wiki/content-pipeline.md](docs/wiki/content-pipeline.md) |
| Work on the API / database | [docs/wiki/backend.md](docs/wiki/backend.md) |
| Work on the game / UI | [docs/wiki/frontend.md](docs/wiki/frontend.md) |
| Improve game feel, graphics, plan for 3D | [docs/wiki/game-stack.md](docs/wiki/game-stack.md) |
| Run or write tests (we work TDD) | [docs/wiki/testing.md](docs/wiki/testing.md) |
| Deploy to AWS | [docs/wiki/deployment-aws.md](docs/wiki/deployment-aws.md) |
| Read the research behind decisions | [research/](research/README.md) — tech + learning-science streams |
| Replace/extend the course content | [curriculum/](curriculum/) + [guide](docs/wiki/getting-started.md#replacing-the-placeholder-curriculum) |
| Contribute with an AI agent | [CLAUDE.md](CLAUDE.md) — rules, commands, repo map |

The documentation under `docs/wiki/` is an LLM wiki: written to be equally
useful to human contributors and AI agents, one topic per page, kept in sync
with the code in the same commit.

## Status

Stage 1 vertical slice is complete and tested: a student can create a
profile, get a personalized world, play three missions (variables,
conditionals, loops) in a 2D map, write real Python against hidden tests,
receive escalating hints and remediation, and finish a coherent story arc.
Next: importing the full Python course, more missions, first deployment —
see [stages.md](docs/wiki/stages.md) for the live list.
