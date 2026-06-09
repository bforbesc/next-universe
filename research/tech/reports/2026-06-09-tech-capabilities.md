# Tech Capabilities Report — 2026-06-09

Previous report: none (inaugural) | Current stage: **Stage 1** (single game, predetermined content)

## Executive summary

- **Phaser 4.0 "Caladan" shipped 2026-04-10** (4.1 on 2026-04-30): brand-new WebGL renderer, unified filter system, `SpriteGPULayer` (up to 1M sprites per draw call). We are on Phaser 3.88 — plan a migration spike during the Stage 1→2 asset/game-feel pass, not now.
- **WebGPU is production-ready in the browser**: three.js ships a zero-config `WebGPURenderer` with automatic WebGL fallback; ~95% of browsers are WebGPU-capable. react-three-fiber v9 supports async renderer init but full WebGPU support was still maturing as of early 2026. The 3D option in our game-stack ladder is getting cheaper every quarter.
- **Frontier models comfortably cover Stage 3**: spring 2026 saw a release burst (Claude Opus 4.7→4.8, GPT-5.5, Gemini 3.5 Flash, DeepSeek V4 Pro at an MIT license + ~75% price cut). SWE-bench-class coding is at 74–80%. Schema-constrained mission generation is well within capability; cost direction is firmly down.
- **Academic work converges on our architecture**: 2026 papers on schema-governed LLM narrative pipelines and dependency-driven quest generation validate the "LLM fills validated schemas inside a deterministic engine" approach — and document the failure mode we already gate against (structurally invalid output).
- **Genie-class world models went public** (Google Project Genie, 2026-01-29: prompt→interactive 3D world at 24fps, AI Ultra subscribers only). Spectacular, but uncontrollable for pedagogy and not embeddable — a Stage 4 horizon-watch item, not a plan change.
- **AI 3D asset generation is prototype-ready** (Meshy: auto-rigging + animation presets; Tripo 3.0: retopology/multi-view; Rodin closest to production-grade) — relevant to game-stack ladder step 6, not before.
- **Pin drift found:** our Pyodide CDN pin is 0.26.4; stable is 0.29.x (Python 3.13/3.14 era). Cheap upgrade, do it in Stage 1.
- **Education-AI tailwind**: adaptive-platform adoption claims (71% of higher-ed institutions by 2026) and LLM-tutoring efficacy studies are accumulating — good for the product thesis; treat specific percentage claims as marketing-grade until traced to primary studies.

## Track A — LLM capabilities & cost

Spring 2026 was a specialization arms race: within ~30 days OpenAI shipped GPT-5.5, Anthropic released Claude Opus 4.7 (4.8 current at time of writing), Google announced Gemini 3.5 Flash, DeepSeek released V4 Pro (MIT license, ~75% price cut), Alibaba unveiled Qwen 3.7 Max ([TeamAI overview](https://teamai.com/blog/large-language-models-llms/the-2026-ai-frontier-model-war/), [Azumo June 2026 rankings](https://azumo.com/artificial-intelligence/ai-insights/top-10-llms-0625)). Coding benchmarks cluster at 74–80% SWE-bench-class ([LM Council benchmarks](https://lmcouncil.ai/benchmarks)) — benchmark numbers vary by source and should be treated as directional.

**So what for us:** our generation task (fill `StoryArc`/`Mission` schemas from curriculum + profile) is far below frontier difficulty; reliability and cost both improve without us doing anything. Our `ANTHROPIC_MODEL` env var makes model upgrades a config change. Open-weight price collapse (DeepSeek V4 Pro) is a future cost lever for Stage 3 scale, at the price of re-validating structured-output reliability.

## Track B — LLM × game generation

- **Schema-governed pipelines**: [Game Knowledge Management System (G-KMS)](https://www.mdpi.com/2079-8954/14/2/175) reformulates LLM narrative generation as structured knowledge management — schema-governed generation, normalization-based repair, engine-aligned admission. This is independent confirmation of our core principle (LLM output is untrusted until validated/verified).
- **Dependency-driven generation**: [From World-Gen to Quest-Line](https://arxiv.org/html/2604.25482) decomposes RPG generation into staged prompts with structured intermediate representations (world → NPCs → quests) — same shape as our arc-then-missions chaining; worth mining for prompt structure when tuning Stage 3.
- **Engine-coupled generation**: [LLMs in Game Development](https://arxiv.org/pdf/2603.27896) notes generated elements increasingly couple to rule execution/progression (not decoration) — our "concept is the in-world mechanism" requirement is the pedagogical version of this.
- **Multi-agent 3D generation**: [AutoUE](https://arxiv.org/pdf/2603.07106) generates Unreal games via multi-agent systems — early-stage, Stage 4-relevant.
- **World models**: Genie 3 went public as [Project Genie](https://www.theregister.com/2026/01/29/googles_project_genie_ai) (2026-01-29; [Engadget](https://www.engadget.com/ai/googles-project-genie-lets-you-create-your-own-3d-interactive-worlds-183646428.html), [Wikipedia](https://en.wikipedia.org/wiki/Genie_(world_model))): prompt/image → navigable, consistent 3D world at 24fps, US AI-Ultra subscribers only. No API for controllable, curriculum-bound experiences. **Verdict: watch.** The Stage 4 path that stays sound is constrained DSL/format generation with verification gates — world models don't yet offer the determinism pedagogy needs.

## Track C — Browser game stacks

- **Phaser 4.0.0 "Caladan", 2026-04-10** ([release](https://phaser.io/download/release/v4.0.0), [GameFromScratch](https://gamefromscratch.com/phaser-4-released/)); 4.1.0 "Salusa" 2026-04-30 ([release](https://phaser.io/download/release/v4.1.0)). New node-based WebGL renderer (proper state management, context-loss handling), unified Filter system, `SpriteGPULayer` (~1M sprites/draw call, claimed up to 100× faster), simplified lighting ([3 vs 4 comparison](https://phaser.io/news/2026/05/phaser-3-vs-phaser-4)). Migration is a real port (renderer pipeline replaced).
- **three.js / WebGPU**: `WebGPURenderer` importable zero-config since r171 (Sep 2025) with automatic WebGL fallback; WebGPU now supported in Chrome, Edge, Firefox, Safari incl. iOS; ~95% capable browsers ([what changed in 2026](https://www.utsubo.com/blog/threejs-2026-what-changed), [migration checklist](https://www.utsubo.com/blog/webgpu-threejs-migration-guide)). R3F v9 supports async `gl` (needed for WebGPU init) but full WebGPU support still maturing as of early 2026 ([v9 migration guide](https://r3f.docs.pmnd.rs/tutorials/v9-migration-guide), [R3F vs three.js 2026](https://www.creativedevjobs.com/blog/react-three-fiber-vs-threejs)).

**So what:** Stage 1 stays on Phaser 3 (stability > shiny). The Stage 1→2 asset/feel pass is the right moment for a Phaser 4 spike (check plugin ecosystem + school-laptop perf). For the eventual 3D format, three.js+WebGPU with WebGL fallback is maturing on schedule — re-check R3F WebGPU status next report.

## Track D — Asset generation

Text/image→3D is prototype-ready, production-iffy: [Meshy](https://www.meshy.ai/blog/best-ai-tools-for-3d-game-assets) (auto-rigging, 500+ animation presets — vendor source), Tripo 3.0 (retopology, mesh optimization, multi-view; [comparison](https://www.tripo3d.ai/compare/tripo-vs-meshy) — vendor source), Rodin/Hyper3D rated closest to drop-in production assets by an [independent test of 9 tools](https://www.indiehackers.com/post/best-ai-3d-model-generator-in-2026-i-tested-9-of-the-best-and-here-is-what-i-found-70ecab1a0a). Consensus: prototype quality easy, hero assets still need human cleanup.

**So what:** nothing to adopt now (we use procedural 2D shapes deliberately). When the asset pass arrives (ladder step 1), 2D sprite/tile generation per theme is the relevant capability; 3D asset gen matters only at ladder step 5+. Pricing/licensing review needed at adoption time.

## Track E — Code execution & sandboxing

Pyodide stable is **0.29.4** ([docs](https://pyodide.org/en/stable/index.html), [GitHub](https://github.com/pyodide/pyodide)); ecosystem mature (NumPy/pandas/matplotlib in-browser, JupyterLite/PyScript adoption; Python 3.14-era). **Our pin in `frontend/public/pyodide-worker.js` is 0.26.4** — upgrade is low-risk (our harness uses only stdlib) and brings newer Python + perf fixes.

## Track F — AI in education

LLM tutoring/adaptive learning adoption is accelerating: claims of 71% of higher-ed institutions deploying adaptive platforms by 2026 and ~42% learning-outcome improvements from multi-dimensional personalization ([X-Pilot trends report](https://www.x-pilot.ai/blog/future-ai-education-2026-trends-report) — marketing-grade, not verified to primary source). Peer-reviewed/working-paper work on LLM-guided personalized tutoring is appearing ([SSRN: Effective Personalized AI Tutors via LLM-Guided RL](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6423358), [higher-ed effectiveness study](https://www.rcresearcharchive.com/index.php/Journal/article/view/850)).

**So what:** tailwind for the thesis; the actionable nugget is that personalization of *pacing, modality and feedback tone* (not just difficulty) shows the strongest claimed gains — our schema already carries difficulty + tone-bearing fields (mentor voice, feedback), pacing adaptation is a Stage 3 work item fed by our `submissions` telemetry.

## Pin drift check

| Pin | Ours | Current | Action |
|---|---|---|---|
| Pyodide (`public/pyodide-worker.js`) | 0.26.4 | 0.29.4 | **Upgrade** (low risk, stdlib-only harness) |
| Phaser (`frontend/package.json`) | ^3.88 | 4.1.0 | **Hold**; spike at Stage 1→2 asset pass |
| Next.js | ^15.3 | 15.x line current | Hold |
| `ANTHROPIC_MODEL` default | `claude-opus-4-8` | current Opus tier | Hold; consider Sonnet-tier for cost when Stage 3 volume starts |

## Recommendations

| Action | Stage | Effort | Verdict |
|---|---|---|---|
| Bump Pyodide pin to 0.29.x and run harness tests | 1 | ~30 min | **Adopt** |
| Phaser 4 migration spike (renderer port, plugin check, low-end perf) | 1→2 | 1–2 days | **Spike at asset pass** |
| Mine dependency-driven prompt-pipeline papers when tuning Stage 3 prompts | 3 prep | hours | **Adopt at Stage 3** |
| Track R3F WebGPU support monthly; prototype a 3D format only after engagement data justifies | 3+ | — | **Watch** |
| Genie-class world models | 4 | — | **Watch** (no controllability/API for pedagogy) |
| Open-weight models (DeepSeek V4 Pro) as Stage-3 cost lever | 3 | eval needed | **Watch** (re-validate structured outputs first) |
| AI 2D asset generation per theme | 1→2 | days | **Spike at asset pass** |

## Sources

- [Phaser v4.0.0 release](https://phaser.io/download/release/v4.0.0) · [v4.1.0](https://phaser.io/download/release/v4.1.0) · [Phaser 3 vs 4](https://phaser.io/news/2026/05/phaser-3-vs-phaser-4) · [GameFromScratch review](https://gamefromscratch.com/phaser-4-released/)
- [three.js 2026 changes](https://www.utsubo.com/blog/threejs-2026-what-changed) · [WebGPU migration checklist](https://www.utsubo.com/blog/webgpu-threejs-migration-guide) · [R3F v9 migration guide](https://r3f.docs.pmnd.rs/tutorials/v9-migration-guide) · [R3F vs three.js 2026](https://www.creativedevjobs.com/blog/react-three-fiber-vs-threejs)
- [G-KMS: schema-governed LLM pipeline (MDPI)](https://www.mdpi.com/2079-8954/14/2/175) · [World-Gen to Quest-Line (arXiv)](https://arxiv.org/html/2604.25482) · [LLMs in Game Development (arXiv)](https://arxiv.org/pdf/2603.27896) · [AutoUE (arXiv)](https://arxiv.org/pdf/2603.07106)
- [Project Genie — The Register](https://www.theregister.com/2026/01/29/googles_project_genie_ai) · [Engadget](https://www.engadget.com/ai/googles-project-genie-lets-you-create-your-own-3d-interactive-worlds-183646428.html) · [Genie — Wikipedia](https://en.wikipedia.org/wiki/Genie_(world_model))
- [TeamAI frontier model war](https://teamai.com/blog/large-language-models-llms/the-2026-ai-frontier-model-war/) · [LM Council benchmarks](https://lmcouncil.ai/benchmarks) · [Azumo June 2026 LLM rankings](https://azumo.com/artificial-intelligence/ai-insights/top-10-llms-0625)
- [Meshy: best AI tools for 3D game assets](https://www.meshy.ai/blog/best-ai-tools-for-3d-game-assets) · [Tripo vs Meshy](https://www.tripo3d.ai/compare/tripo-vs-meshy) · [Indie Hackers 9-tool test](https://www.indiehackers.com/post/best-ai-3d-model-generator-in-2026-i-tested-9-of-the-best-and-here-is-what-i-found-70ecab1a0a)
- [Pyodide docs (0.29.4)](https://pyodide.org/en/stable/index.html) · [Pyodide GitHub](https://github.com/pyodide/pyodide)
- [X-Pilot AI-in-education 2026 trends](https://www.x-pilot.ai/blog/future-ai-education-2026-trends-report) · [SSRN LLM-guided tutoring](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6423358) · [LLM tutoring effectiveness study](https://www.rcresearcharchive.com/index.php/Journal/article/view/850)
