# Game Stack Track

Cross-cutting track across all [stages](stages.md): continuously improve game
feel, graphics and dynamics **without coupling the content pipeline to any
renderer**. The `format` seam ([architecture.md](architecture.md) §seams) is
what makes renderer evolution safe: content is schema-shaped data; renderers
interpret formats.

## Today (Stage 1)

Phaser 3 (`components/GameCanvas.tsx`), procedurally drawn (no asset files),
theme-recolored. Deliberately minimal: Stage 1–3 product risk is content
quality, not graphics.

## Improvement ladder (pull these in as stages progress, in rough order)

| Step | What | When justified |
|---|---|---|
| 1 | Asset pass: sprite sheets, tilemaps, parallax backgrounds per theme, character sprites with walk animations | Stage 1 polish / first user tests |
| 2 | Game feel: tweens, particles (mission complete bursts), screen shake, SFX/music per theme, typewriter dialogue | Stage 1–2 |
| 3 | World structure: multi-area maps (one area per module), NPCs with dialogue trees (mentor walks the world), collectibles tied to concepts | Stage 2 |
| 4 | New 2D formats: puzzle-grid, dialogue-driven, resource-sim — each a new `format` id + renderer | Stage 2–3 |
| 5 | **3D / richer engines** — see below | Stage 3+, evidence-driven |
| 6 | Generated assets (image models for scene art, sprites per theme) stored in S3 at generation time | Stage 3+ |

## 3D and engine options (evaluate when engagement data justifies it)

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| Three.js / react-three-fiber | Browser-native, fits Next.js, incremental adoption (one format can be 3D while others stay 2D) | Build-your-own game engine pieces | First choice for browser 3D |
| Babylon.js | Fuller engine (physics, GUI, inspector), browser-native | Heavier; less React-idiomatic | Strong alternative |
| PlayCanvas | Engine + editor, browser-native | Editor-centric workflow, hosted tooling | If a visual editor becomes important |
| Unity (WebGL or native) | Best-in-class feel, mobile, NPCs, animation tooling | Separate build pipeline, large payloads, team skill set, breaks browser-first iteration speed | Only for a polished demo or mobile push; revisit at Stage 3/4 |

Decision rule: **renderers may change; the content contract may not.** Any 3D
move must consume the same schema-shaped, verified content via a new `format`
id. If a renderer needs different content fields, that's a new format schema —
never a bypass of validation/verification.

## Invariants for this track

- Code challenges remain sandboxed in the browser (or a server runner later) —
  the renderer never executes student code itself.
- A format renderer must run on a mid-range laptop in a school network:
  budget payload sizes (Pyodide is already ~10MB; keep engines lazy-loaded per
  format).
- Theme is data: new themes must not require renderer changes (colors/assets
  keyed by theme id).
