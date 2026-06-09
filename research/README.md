# Research — Tech Capabilities Tracking

Active research on the technology this platform rides on: LLM capabilities and
game stacks evolve fast, and stage transitions ([../docs/wiki/stages.md](../docs/wiki/stages.md))
should be triggered by **evidence of capability**, not guesses. This folder is
the project's memory of that evidence.

**To run a new research pass, invoke the project skill: `/tech-research`**
(defined in `.claude/skills/tech-research/SKILL.md`). The skill reads the
previous report, searches each track, and writes the next dated report here.

## Layout

```
research/
  README.md            this charter + report index
  reports/             dated reports, append-only history (never edit old ones)
    YYYY-MM-DD-tech-capabilities.md
```

## Research tracks

Every report covers these tracks (add a track only by updating this charter):

| # | Track | What to watch |
|---|---|---|
| A | **LLM capabilities & cost** | frontier model releases, coding/agentic benchmarks, structured-output reliability, context windows, token prices, multimodal |
| B | **LLM × game generation** | research + products on schema-governed content generation, quest/narrative pipelines, world models (Genie-class), runtime generation |
| C | **Browser game stacks** | Phaser, three.js/react-three-fiber, Babylon, WebGPU adoption, engine releases relevant to [game-stack.md](../docs/wiki/game-stack.md) |
| D | **Asset generation** | text/image→2D art, →3D models (Meshy/Tripo/Rodin class), rigging/animation, audio/music gen, licensing |
| E | **Code execution & sandboxing** | Pyodide releases, WASM runtimes, server-side sandbox options, our CDN pins |
| F | **AI in education** | adaptive learning evidence, LLM tutoring efficacy studies, market adoption, pedagogy findings worth encoding in prompts |

## Methodology (what makes a report trustworthy)

1. **Read the previous report first** — a report's value is the *delta*.
2. Every claim carries a **source link**; distinguish vendor marketing from
   independent benchmarks/papers and say which is which.
3. Record **version numbers and dates**, not vibes ("Phaser 4.0, 2026-04-10",
   not "Phaser improved").
4. End with **stage-mapped recommendations**: each finding → which stage it
   affects → concrete action (adopt / spike / watch / ignore), cheapest first.
5. Check findings against **our current pins** (Pyodide version in
   `frontend/public/pyodide-worker.js`, Phaser in `frontend/package.json`,
   `ANTHROPIC_MODEL` default in `backend/app/config.py`) and flag drift.
6. History is **append-only**: never rewrite an old report; corrections go in
   the next one.

## Cadence

Monthly, plus an extra pass before any stage transition or major stack
decision (e.g. "do we adopt 3D?").

## Report index (newest first)

| Date | Report | Headline |
|---|---|---|
| 2026-06-09 | [reports/2026-06-09-tech-capabilities.md](reports/2026-06-09-tech-capabilities.md) | Inaugural: Phaser 4 released; WebGPU production-ready; Genie 3 public; Stage-3 generation well within model capability |
