---
name: tech-research
description: Run a tech-capabilities research pass for Next Universe (LLMs, game stacks, asset gen, sandboxing, AI-in-education). Reads the previous report in research/reports/, web-searches each track from the charter, and writes a new dated report with stage-mapped recommendations. Use when asked to run/update research, before stage transitions, or for major stack decisions.
---

# Tech Research Pass

You are producing the next entry in an append-only research history that this
project uses to decide when to move between stages and what stack to bet on.

## Procedure

1. **Load context (mandatory, in this order):**
   - `research/README.md` — the charter: tracks, methodology, report index.
   - The most recent report in `research/reports/` — your job is the **delta**
     since that report, not a from-scratch survey.
   - `docs/wiki/stages.md` — current stage and what each stage needs.
   - Current pins to check for drift: Pyodide version in
     `frontend/public/pyodide-worker.js`, Phaser/Next versions in
     `frontend/package.json`, `ANTHROPIC_MODEL` default in
     `backend/app/config.py`.

2. **Research each track (A–G from the charter)** with web search. For each
   track: what changed since the last report's date? New releases (capture
   exact versions + dates), new benchmarks/papers, price changes, capability
   jumps. Prefer primary sources (release notes, papers, official docs) over
   blog roundups; label vendor marketing as such. If the user asked a focused
   question (e.g. "research 3D engines"), go deep on the relevant track(s) and
   do a light delta-check on the rest.

3. **Write the report** at `research/reports/YYYY-MM-DD-tech-capabilities.md`
   (today's date) with this structure:

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
   ## Track F — AI in education
   ## Track G — Learning science & behavioral psychology
   ## Pin drift check            (our versions vs current; upgrade or hold + why)
   ## Recommendations            (table: action | stage affected | effort | verdict: adopt/spike/watch/ignore)
   ## Sources                    (all links used)
   ```

4. **Update the report index** table in `research/README.md` (newest first,
   one-line headline). Never edit previous reports — corrections belong in the
   new report's delta section.

5. **Surface, don't silently apply.** If a finding implies a code change
   (e.g. a pin bump) or a wiki change (e.g. stage criteria, game-stack
   ladder), list it in Recommendations and tell the user; only apply changes
   the user asked for. Exception: the README index update is part of this skill.

6. Commit the new report + index update (and push if the session's workflow
   pushes), with a message summarizing the headline findings.

## Quality bar

- Every claim has a link; versions and dates are exact.
- Recommendations are stage-mapped and effort-rated; cheapest-first.
- The "so what" matters more than the "what": a finding without a consequence
  for this project is a footnote, not a section.
- Honest uncertainty: if sources conflict (common with benchmark claims), say
  so rather than picking one.
- Track G (learning science) has a higher source bar: meta-analyses and
  systematic reviews from strong outlets; every design recommendation derived
  from it must name the effect it relies on and its approximate effect size.
