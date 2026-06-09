---
name: learning-research
description: Run a learning-research pass for Next Universe (learning science & behavioral psychology, pedagogy for novice programmers, AI-in-education evidence). Reads the charter and previous report in research/learning/, searches for new meta-analyses/systematic reviews, and writes a new dated report where every finding becomes a design implication for the game. Use when asked to research learning/retention/motivation/pedagogy, or before changing hint/feedback/mission design. For LLM/game-stack research use /tech-research instead.
---

# Learning Research Pass

You are producing the next entry in an append-only research history that keeps
this game designed on learning-science evidence, not gamification folklore.

## Procedure

1. **Load context (mandatory, in this order):**
   - `research/README.md` — shared rules for all research.
   - `research/learning/charter.md` — tracks L1–L3 and the **higher source bar**.
   - The most recent report in `research/learning/reports/` — your job is the
     **delta** since that report's date.
   - `docs/wiki/content-pipeline.md` → "Learning-science design rules" — the
     rules currently in force; your report may propose changes to them.
   - `docs/wiki/stages.md` — current stage.

2. **Research each track (L1–L3)** with web search. Source bar: meta-analyses
   and systematic reviews from strong outlets (Educational Psychology Review,
   Psychological Science, npj Science of Learning, ACM ICER/TOCE/SIGCSE,
   Computers & Education); single studies only when no synthesis exists,
   flagged as such; blogs/vendor reports are leads, never evidence.

3. **Write the report** at
   `research/learning/reports/YYYY-MM-DD-learning-science.md` (today's date):

   ```markdown
   # Learning Science Report — YYYY-MM-DD
   Previous report: <link> | Current stage: <from stages.md>

   ## Executive summary          (5-8 bullets: what changed, what we should do)
   ## Delta since last report    (table: finding | track | so what)
   ## Track L1 — Learning science & behavioral psychology
   ## Track L2 — Pedagogy for novice programmers
   ## Track L3 — AI in education: evidence & products
   ## Design-rule review         (current wiki rules still supported? changes proposed?)
   ## Recommendations            (table: action | evidence (effect + size) | stage | effort | adopt/spike/watch/ignore)
   ## Sources
   ```

4. **Every finding ends in a design implication** — which engine feature,
   schema field, prompt rule, or wiki design rule it touches. Each
   recommendation names the effect it relies on and its approximate effect
   size. A finding with no consequence for the product is a footnote.

5. **Update the report index** in `research/learning/charter.md` and the
   "Latest headlines" table in `research/README.md`. Never edit previous
   reports.

6. **Surface, don't silently apply.** Proposed changes to the wiki design
   rules or to hint/feedback/mission mechanics are recommendations for the
   user — only the index updates are part of this skill.

7. Commit the report + index updates (push if the session's workflow pushes),
   message summarizing headline findings.
