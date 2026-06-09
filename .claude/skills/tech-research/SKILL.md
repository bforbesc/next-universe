---
name: tech-research
description: Run a tech-capabilities research pass for Next Universe (LLM capabilities/cost, LLM x game generation, browser game stacks, asset generation, code execution/sandboxing). Reads the charter and previous report in research/tech/, web-searches each track for the delta, writes a new dated report with stage-mapped recommendations and a pin-drift check. Use when asked to research tech/stack capabilities, before stage transitions, or for stack decisions. For learning/pedagogy research use /learning-research instead.
---

# Tech Research Pass

You are producing the next entry in an append-only research history that this
project uses to decide when to move between stages and what stack to bet on.

## Procedure

1. **Load context (mandatory, in this order):**
   - `research/README.md` — shared rules for all research.
   - `research/tech/charter.md` — tracks A–E and stream methodology.
   - The most recent report in `research/tech/reports/` — your job is the
     **delta** since that report's date, not a from-scratch survey.
   - `docs/wiki/stages.md` — current stage and what each stage needs.
   - Current pins (for the drift check): Pyodide version in
     `frontend/public/pyodide-worker.js`, Phaser/Next versions in
     `frontend/package.json`, `ANTHROPIC_MODEL` default in
     `backend/app/config.py`.

2. **Research each track (A–E)** with web search: exact versions + dates of
   new releases, benchmarks/papers, price changes, capability jumps. Prefer
   primary sources; label vendor marketing. If the user asked a focused
   question (e.g. "research 3D engines"), go deep on the relevant track(s)
   and delta-check the rest lightly.

3. **Write the report** at
   `research/tech/reports/YYYY-MM-DD-tech-capabilities.md` (today's date):

   ```markdown
   # Tech Capabilities Report — YYYY-MM-DD
   Previous report: <link> | Current stage: <from stages.md>

   ## Executive summary          (5-8 bullets: what changed, what we should do)
   ## Delta since last report    (table: finding | track | so what)
   ## Track A — LLM capabilities & cost
   ## Track B — LLM × game generation
   ## Track C — Browser game stacks
   ## Track D — Asset generation
   ## Track E — Code execution & sandboxing
   ## Pin drift check            (our versions vs current; upgrade or hold + why)
   ## Recommendations            (table: action | stage | effort | adopt/spike/watch/ignore)
   ## Sources
   ```

4. **Update the report index** in `research/tech/charter.md` (newest first,
   one-line headline) and the "Latest headlines" table in `research/README.md`.
   Never edit previous reports.

5. **Surface, don't silently apply.** Code/wiki changes implied by findings go
   in Recommendations for the user to approve; only the index updates are part
   of this skill.

6. Commit the report + index updates (push if the session's workflow pushes),
   message summarizing headline findings.

## Quality bar

- Every claim has a link; versions and dates are exact.
- Recommendations are stage-mapped and effort-rated, cheapest first.
- The "so what" matters more than the "what" — a finding without a consequence
  for this project is a footnote.
- Honest uncertainty: when sources conflict (common for benchmarks), say so.
