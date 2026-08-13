# DEVELOPMENT-TASK-BY-PHASES.md — Vietlott Statistics & Responsible-Play Advisor

This is the phased build plan for turning this scaffold into a working Claude Skill, following the skill-creator methodology (draft → test → evaluate → iterate → package).

## Phase 1 - Foundation
**Goal:** Honest mathematical framework per game format

**Tasks:**
- [ ] Draft SKILL.md with an explicit rule: never present number 'predictions' as having real predictive power
- [ ] Build per-format (Mega 6/45, Power 6/55, Keno, Max 3D) odds-calculation reference

## Phase 2 - Myth-Busting Education
**Goal:** Debunk common fallacies

**Tasks:**
- [ ] Build gambler's-fallacy and historical-frequency-analysis myth explainer with cited research
- [ ] Add independence-of-draws explainer specific to each format

## Phase 3 - Expected Value Layer
**Goal:** Real math education

**Tasks:**
- [ ] Build expected-value/house-edge calculator explainer using published Vietlott prize structures
- [ ] Add explainer distinguishing jackpot-format vs. Keno/Max 3D odds structures

## Phase 4 - Responsible Play Layer
**Goal:** Safety-first framing

**Tasks:**
- [ ] Build problem-gambling risk-indicator checklist
- [ ] Add Vietnamese-context responsible-gambling resource referral guidance

## Phase 5 - Testing & Polish
**Goal:** Validate refusal + education balance

**Tasks:**
- [ ] Test that the skill refuses to produce 'predicted winning numbers' while still being maximally helpful with real math
- [ ] Package with disclaimers

## Final Step — Packaging

- [ ] Write the actual `SKILL.md` (name + description + body) based on the specification in `PROJECT-detail.md`
- [ ] Build any `references/`, `scripts/`, or `assets/` the skill needs
- [ ] Run the skill-creator evaluation loop (test prompts, review, iterate)
- [ ] Package the finished skill for distribution
