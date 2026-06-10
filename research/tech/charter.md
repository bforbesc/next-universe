# Tech Research — Charter

Tracks the technology this platform rides on: LLMs and game stacks evolve
fast, and moving across [stages](../../docs/wiki/stages.md) should be
triggered by evidence of capability. Run a pass with the **`/tech-research`**
skill. Shared rules (append-only history, delta reports, sourcing, recommendation
format) live in the [research index](../README.md).

## Tracks

| # | Track | What to watch |
|---|---|---|
| A | **LLM capabilities & cost** | frontier model releases, coding/agentic benchmarks, structured-output reliability, context windows, token prices, multimodal |
| B | **LLM × game generation** | research + products on schema-governed content generation, quest/narrative pipelines, world models (Genie-class), runtime generation |
| C | **Browser game stacks** | Phaser, three.js/react-three-fiber, Babylon, WebGPU adoption, engine releases relevant to [game-stack.md](../../docs/wiki/game-stack.md) |
| D | **Asset generation** | text/image→2D art, →3D models (Meshy/Tripo/Rodin class), rigging/animation, audio/music gen, licensing |
| E | **Code execution & sandboxing** | Pyodide releases, WASM runtimes, server-side sandbox options |

## Stream-specific methodology

- **Pin drift check every pass** — compare findings against our actual
  versions: Pyodide in `frontend/public/pyodide-worker.js`, Phaser/Next in
  `frontend/package.json`, `ANTHROPIC_MODEL` default in
  `backend/app/config.py`. Recommend upgrade or hold, with why.
- Prefer primary sources: release notes, papers, official docs; benchmark
  numbers vary by source — treat as directional and say so.

## Report index (newest first)

| Date | Report | Headline |
|---|---|---|
| 2026-06-09 | [reports/2026-06-09-tech-capabilities.md](reports/2026-06-09-tech-capabilities.md) | Inaugural: Phaser 4.0/4.1 released Apr 2026 (hold, spike at asset pass); WebGPU production-ready in three.js; frontier models comfortably cover Stage-3 generation, prices falling; Genie 3 public (watch); Pyodide pin drift 0.26.4 → 0.29.x |
