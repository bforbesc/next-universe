# Research — Index

The project's evidence memory. Stage transitions and design decisions
([../docs/wiki/stages.md](../docs/wiki/stages.md)) are driven by what we
*know*, and this folder is the append-only history of how we know it.

Two independent research streams, each with its own charter, report history
and Claude skill:

| Stream | Charter | Reports | Skill | Covers |
|---|---|---|---|---|
| **Tech capabilities** | [tech/charter.md](tech/charter.md) | [tech/reports/](tech/reports/) | `/tech-research` | LLM capabilities & cost, LLM × game generation, browser game stacks, asset generation, code execution & sandboxing |
| **Learning research** | [learning/charter.md](learning/charter.md) | [learning/reports/](learning/reports/) | `/learning-research` | learning science & behavioral psychology, pedagogy for novice programmers, AI-in-education evidence |

## How to run a research pass

Ask an agent to run `/tech-research` or `/learning-research` (skills in
`.claude/skills/`). Each skill reads its charter and the previous report in
its stream, researches the delta, writes a new dated report, and updates its
stream's report index in the charter.

## Shared rules (both streams)

- **History is append-only.** Never edit a published report; corrections go in
  the next report's delta section.
- **Reports are deltas.** Read the previous report first; the value of a new
  report is what changed.
- **Every claim has a source link**; versions and dates are exact; vendor
  marketing is labeled as such.
- **Findings end in recommendations** mapped to [stages](../docs/wiki/stages.md):
  adopt / spike / watch / ignore, effort-rated, cheapest first.
- **Surface, don't silently apply**: recommendations that imply code or wiki
  changes are listed for the user, not auto-applied.
- File naming: `reports/YYYY-MM-DD-<topic>.md`.

## Cadence

Monthly per stream, plus a focused pass before any stage transition or major
decision in that stream's territory (stack choice, pedagogy change).

## Latest headlines

| Date | Stream | Report | Headline |
|---|---|---|---|
| 2026-06-09 | learning | [learning-science](learning/reports/2026-06-09-learning-science.md) | Retrieval/spacing strongest effects → callback + spaced review; hint 1 should be opt-in; Parsons widget for remediation; intrinsic > extrinsic gamification |
| 2026-06-09 | tech | [tech-capabilities](tech/reports/2026-06-09-tech-capabilities.md) | Phaser 4 released; WebGPU production-ready; Genie 3 public (watch); Stage-3 generation well within model capability; Pyodide pin drift |

Full per-stream indexes live in each charter.
