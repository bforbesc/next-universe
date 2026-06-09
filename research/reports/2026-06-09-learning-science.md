# Learning Science Report — 2026-06-09 (focused: Track G inaugural)

Previous report: [2026-06-09-tech-capabilities.md](2026-06-09-tech-capabilities.md) (Tracks A–F) | Current stage: **Stage 1**

Focused pass establishing Track G (learning science & behavioral psychology):
what the strongest available evidence says about learning and retention, and
what each finding means for this game's design. Effect sizes are reported
where sources give them; Track G's source bar is meta-analyses/systematic
reviews where possible.

## Executive summary

- **Retrieval practice and spacing are the most robust effects in the field** — and our game currently teaches each concept once and never returns to it. The cheapest, highest-evidence design win available: later missions should *require* earlier concepts (callback challenges), and review missions should be spaced across sessions (Stage 2/3).
- **Immediate full hints may be hurting learning.** Delayed feedback and "desirable difficulties" research suggests our hint-on-first-failure is too generous; make hint 1 opt-in and let students retry unaided first.
- **Game-based learning works, but intrinsic > extrinsic**: meta-analyses show moderate-to-large effects, and that points/badges/leaderboards mostly drive *extrinsic* motivation. Our story-progression-as-reward design is the right bet — keep it, and resist leaderboard features.
- **Worked examples and Parsons problems are the best-evidenced scaffolds for novice programmers** — both map cleanly onto our remediation system and the Stage 2/3 widget library.
- **Self-determination theory (competence, autonomy, relatedness) is the design lens** — our theme choice (autonomy), difficulty adaptation + visible progress (competence), and mentor character (relatedness) already align; name it explicitly in the content quality bar.

## Findings

### 1. Retrieval practice & spaced repetition (strongest evidence)

- Math learning meta-analysis (Educational Psychology Review, 2025): spaced vs massed practice shows a robust small-to-medium effect (g ≈ 0.28, 27 studies) — [Springer](https://link.springer.com/article/10.1007/s10648-025-10035-1).
- Medical education systematic review + meta-analysis (2026) supports spaced repetition for objective test performance — [Wiley](https://asmepublications.onlinelibrary.wiley.com/doi/10.1111/tct.70353), [PubMed](https://pubmed.ncbi.nlm.nih.gov/41601436/); superiority over repeated study also found in practicing physicians — [PubMed](https://pubmed.ncbi.nlm.nih.gov/39250798/).
- Honest nuance: single-paper meta-analyses across nine intro STEM courses found mixed in-course effects ("glass half full or half empty") — [IJ STEM Ed](https://link.springer.com/article/10.1186/s40594-024-00468-5). Lab effects are robust; classroom implementation quality matters.

**Design implication:** testing *is* learning — our test-on-every-mission loop is already retrieval practice. What's missing is **re-retrieval over time**: (a) later missions' hidden tests should include the earlier concept in service of the new one (variables inside the loops mission — partially true today), (b) explicit "callback" beats within missions, (c) spaced review missions between sessions, scheduled from `mission_states` timestamps (Stage 3).

### 2. Feedback timing, desirable difficulties, productive failure

- Immediate feedback boosts short-term performance but can produce inferior long-term learning; delayed feedback acts as a desirable difficulty — [pretesting/feedback-timing study (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292081/), [EFL feedback-timing lab study (Nature HSSC)](https://www.nature.com/articles/s41599-024-03983-6), [performance-feedback timing (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S0361368216300770).
- Productive failure: initial struggle followed by structured guidance deepens understanding — provided the challenge stays within reach — [integrative review (Frontiers in Education)](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2018.00049/full), [Bjork's desirable difficulties](https://www.structural-learning.com/post/desirable-difficulties) (secondary source).

**Design implication:** don't hand over hint 1 automatically on the first failure. Let the failure feedback (story + technical, no solution direction) stand alone, make hints an explicit button ("Ask ARIA for help"), and keep the existing escalation behind it. Our remediation-after-3-failures already implements "structured guidance after struggle"; the threshold protects "within reach".

### 3. Novice programming pedagogy (cognitive load)

- Cognitive Load Theory is the organizing framework for intro programming — [review (ACM TOCE)](https://dl.acm.org/doi/10.1145/3483843).
- Worked examples reduce extraneous load and improve retention for novices; explanation type and learner motivation moderate the effect — [ACM TOCE 2025](https://dl.acm.org/doi/full/10.1145/3732791).
- Parsons problems (reorder given code blocks) are more efficient than writing equivalent code at similar learning, with lower cognitive load; effects vary with self-efficacy — [CHI study](https://dl.acm.org/doi/fullHtml/10.1145/3411764.3445292), [ICER 2024](https://dl.acm.org/doi/10.1145/3632620.3671110), [scaffolding variations (arXiv)](https://arxiv.org/pdf/2512.22407).

**Design implication:** (a) for `prior_knowledge == "none"`, show a worked example (themed, parallel to the task — not the solution) before the task — a personalization lever the schema can carry; (b) a **Parsons-problem widget is the ideal remediation mechanic**: when a student is stuck, "rebuild the spell from these fragments" is both story-friendly and the best-evidenced scaffold — first candidate for the Stage 2/3 widget library.

### 4. Game-based learning & motivation (self-determination theory)

- Meta-analyses: game-based learning shows moderate-to-large effects on cognitive, motivational and engagement outcomes — [natural sciences meta-analysis (MDPI Education, 2026)](https://www.mdpi.com/2227-7102/16/1/122), [early childhood meta-analysis (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11018941/), [gamification of learning meta-analysis (Educ Psych Review)](https://link.springer.com/article/10.1007/s10648-019-09498-w).
- K-12 gamification meta-analysis (Psychology in the Schools, 2025): gamification's effect is **stronger on extrinsic than intrinsic motivation** — points/badges/leaderboards promote controlled motivation; ownership, mastery and social connection promote internalized engagement — [Wiley](https://onlinelibrary.wiley.com/doi/10.1002/pits.70056).
- SDT (competence, autonomy, relatedness) as the design frame for game mechanics — [LM-GM under SDT (arXiv)](https://arxiv.org/pdf/1805.08053).

**Design implication:** our core bet — story progression as the reward, concept as the in-world mechanism — is the intrinsic-motivation design the evidence favors. Codify as design rules: *no leaderboards/badges as primary loops*; autonomy = theme + (later) route choices; competence = difficulty adaptation + visible progress map; relatedness = mentor voice now, safe social features later.

## Recommendations

| Action | Evidence | Stage | Effort | Verdict |
|---|---|---|---|---|
| Make hint 1 opt-in (button), keep escalation behind it | feedback timing / desirable difficulties | 1 | small (UI + tests) | **Adopt** |
| Encode "callback" pattern in content: each mission's tests also exercise one earlier concept; add to prompt rules + golden content | retrieval practice | 1 | small-medium | **Adopt** |
| Worked-example variant before the task when `prior_knowledge == "none"` | worked-example effect | 1–3 | medium (schema field + prompts + golden content) | **Adopt at next content pass** |
| Parsons-problem widget as remediation mechanic | Parsons/cognitive load | 2–3 | medium (first widget-library entry) | **Spike at Stage 2** |
| Spaced review missions scheduled from telemetry | spacing effect | 3 | medium | **Adopt at Stage 3** |
| Design rule: no leaderboards/badges as primary motivation; story progression is the reward | SDT / gamification meta-analyses | all | doc-only | **Adopt now** (added to wiki) |
| Pretesting ("try before taught") mission variant | pretesting effect | 3 | medium | **Watch** (evidence promising, design risk for confidence of young beginners) |

## Sources

- [Spacing & retrieval for mathematics — meta-analysis, Educ Psych Review 2025](https://link.springer.com/article/10.1007/s10648-025-10035-1)
- [Spaced repetition in medical education — systematic review & meta-analysis, 2026](https://asmepublications.onlinelibrary.wiley.com/doi/10.1111/tct.70353) · [PubMed](https://pubmed.ncbi.nlm.nih.gov/41601436/) · [physicians RCT](https://pubmed.ncbi.nlm.nih.gov/39250798/)
- [Spaced retrieval in nine STEM courses — IJ STEM Education](https://link.springer.com/article/10.1186/s40594-024-00468-5)
- [Pretesting effect & feedback timing — PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292081/) · [Feedback timing & retrieval practice — Nature HSSC](https://www.nature.com/articles/s41599-024-03983-6) · [Feedback timing & performance — ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0361368216300770)
- [Difficulties and confusion in learning — integrative review, Frontiers](https://www.frontiersin.org/journals/education/articles/10.3389/feduc.2018.00049/full) · [Bjork's desirable difficulties (secondary)](https://www.structural-learning.com/post/desirable-difficulties)
- [Cognitive Load Theory in computing education — ACM TOCE review](https://dl.acm.org/doi/10.1145/3483843) · [Worked examples, explanation types & motivation — ACM TOCE 2025](https://dl.acm.org/doi/full/10.1145/3732791)
- [Adaptive Parsons problems vs code writing — CHI](https://dl.acm.org/doi/fullHtml/10.1145/3411764.3445292) · [Parsons scaffolding in integrated science — ICER 2024](https://dl.acm.org/doi/10.1145/3632620.3671110) · [Parsons variations — arXiv](https://arxiv.org/pdf/2512.22407) · [Parsons & self-efficacy — arXiv](https://arxiv.org/html/2311.18115v1)
- [GBL in natural sciences — meta-analysis, MDPI Education 2026](https://www.mdpi.com/2227-7102/16/1/122) · [Gamification & K-12 motivation — meta-analysis, Psychology in the Schools 2025](https://onlinelibrary.wiley.com/doi/10.1002/pits.70056) · [Gamification of learning — meta-analysis, Educ Psych Review](https://link.springer.com/article/10.1007/s10648-019-09498-w) · [GBL in early childhood — meta-analysis, PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11018941/)
- [Learning & game mechanics under SDT — arXiv](https://arxiv.org/pdf/1805.08053)
