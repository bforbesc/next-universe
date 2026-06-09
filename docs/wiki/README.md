# LLM Wiki — Next Universe

Documentation written for agents (and humans) working on this codebase: one
topic per page, facts over prose, explicit file paths, cross-linked. When code
and wiki disagree, trust the code and fix the wiki in the same change.

## Pages

| Page | Topic |
|---|---|
| [stages.md](stages.md) | **Start here.** Product roadmap: Stage 1→4, current status, what belongs in which stage |
| [architecture.md](architecture.md) | System overview, trust boundaries, data flow, extension seams |
| [content-pipeline.md](content-pipeline.md) | Curriculum → generation (LLM/template) → verification → persistence |
| [backend.md](backend.md) | FastAPI service: endpoints, data model, services |
| [frontend.md](frontend.md) | Next.js app: pages, components, Pyodide runner |
| [game-stack.md](game-stack.md) | Game experience track: renderer today, path to richer 2D/3D |
| [testing.md](testing.md) | TDD workflow, what each suite pins down, how to run |
| [deployment-aws.md](deployment-aws.md) | AWS mapping, env config, what changes at deploy time (nothing in code) |

## Maintenance rules

- Update the wiki **in the same commit** as the behavior it documents.
- Keep pages short; split rather than scroll.
- Every claim should be checkable against a file path or test.
- Stage scope questions are settled by [stages.md](stages.md) — if a feature
  request belongs to a later stage, build only the seam, not the feature.
