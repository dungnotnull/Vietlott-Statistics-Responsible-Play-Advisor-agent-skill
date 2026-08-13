# RESEARCH-PAPER-KNOWLEDGE-BRAIN.md — Vietlott Statistics & Responsible-Play Advisor

> The applied research brain for this skill. Where `SECOND-BRAIN-KNOWLEDGE-PAPER.md` is the curated reading list, **this file is the distilled, operational brain**: for each source we extract a concrete *operational principle* and map it to the exact skill component (reference file, tool, or hook) that applies it. The result is a traceable chain from peer-reviewed finding -> skill behaviour, so every recommendation the skill makes is auditable back to its evidence base.

**Sourcing note:** Citations were compiled from general subject-matter knowledge to give the skill a strong research foundation. Before relying on any specific citation in a formal deliverable, verify the exact title, year, and venue independently. The principles below reflect established, broadly-replicated findings in probability theory and gambling studies; the mapping is the skill's own contribution.

**How this brain is used by the skill:**
- The `quality_check` post-processing hook verifies that substantive answers cite or paraphrase the framework(s) relevant to the route, drawn from this brain.
- Each sub-advisor's reference file opens with a "Foundation" block that names the papers feeding it; those names live here with full operational detail.
- The `Research-to-Skill Application Matrix` (below) is the master traceability table.

---

## Methodology 1 — Combinatorial probability theory (per-format odds)

### P1. Feller, W. (1968). *An Introduction to Probability Theory and Its Applications, Vol. 1* (3rd ed.). Wiley.
- **Core finding:** Lottery outcomes are modelled exactly by combinatorial counting; for a fair single-pool draw, every r-subset of an n-pool is equally likely, so P(match k) = C(r,k)·C(n−r,r−k)/C(n,r). This is the rigorous, verifiable basis for all odds.
- **Methodology:** Axiomatic probability + combinatorics; sample-space enumeration.
- **Operational principle:** Always derive odds from the sample space with binomial coefficients; show the derivation so a user can verify it; never assert odds without showing the math.
- **Applied in:** `references/combinatorics.md` (per-format derivation table); `scripts/combinatorics.py` (`single_pool_match_odds`, `bonus_pool_match_odds`); the `calculate_odds` tool output's `calculation` field.

### P2. Haigh, J. (1997). *Taking Chances: Winning with Probability*. Oxford University Press.
- **Core finding:** Expected value for a lottery ticket is the probability-weighted sum of prizes minus cost; because operators pay out a fixed fraction, EV is reliably negative across game types and "1 in N" framing is more intuitive than raw probability.
- **Methodology:** Applied probability; worked examples across game formats.
- **Operational principle:** Compute EV in the player's currency; express odds as "1 in N"; show the per-tier contribution lines; frame spending as a guaranteed average loss, not a possible win.
- **Applied in:** `references/expected-value.md`; `scripts/expected_value.py` (`calculate_expected_value`, `long_term_projection`); the "1_in_N" odds format in `config/feature-flags.json`.

### P3. Forrest, D., Gulley, O., & Simmons, R. (2000). Testing for Rational Expectations in the UK National Lottery. *Applied Economics*, 32(13).
- **Core finding:** Number-selection patterns of real lottery players reflect systematically biased beliefs (e.g., clustering on dates), not rational EV-maximising behaviour; this depresses pari-mutuel EV for those selections when they win (shared jackpots).
- **Methodology:** Econometric analysis of actual ticket data vs random baselines.
- **Operational principle:** Warn that "lucky number"/birthday selection (1–31) raises pari-mutuel split risk and lowers EV — a quantifiable cost of the illusion of control.
- **Applied in:** `references/cognitive-biases.md` §4 (illusion of control) and `references/expected-value.md` (pari-mutuel special case); `tests/test_cases.md` D2.

---

## Methodology 2 — Independence of random events / law of large numbers

### P4. Tversky, A., & Kahneman, D. (1971). Belief in the Law of Small Numbers. *Psychological Bulletin*, 76(2).
- **Core finding:** People expect small samples to "look like" the population (even distribution), so short-run clustering is misread as a meaningful pattern — the root of hot/cold and "due" beliefs.
- **Methodology:** Cognitive experiments on subjective probability.
- **Operational principle:** Explicitly name "belief in the law of small numbers" when debunking soi cầu/hot-cold; explain that clustering is the *expected* signature of true randomness, not a signal.
- **Applied in:** `references/cognitive-biases.md` §1–3; `mythbust` route canonical responses.

### P5. Kahneman, D., & Tversky, A. (1972). Subjective Probability: A Judgment of Representativeness. *Cognitive Psychology*, 3(3).
- **Core finding:** Representativeness heuristic: people judge probability by resemblance to a stereotype, so sequences like 1-2-3-4-5-6 are wrongly judged "less likely" than messy ones.
- **Methodology:** Probability-judgment experiments.
- **Operational principle:** State that every specific combination has identical probability (e.g., 1 in 8,145,060 for Mega); "looks random" is irrelevant.
- **Applied in:** `references/cognitive-biases.md` §3; `tests/test_cases.md` D2.

### P6. Clotfelter, C., & Cook, P. (1993). The 'Gambler's Fallacy' in Lottery Play. *Management Science*, 39(12).
- **Core finding:** Real lottery players bet *less* on numbers that recently won, demonstrating the gambler's fallacy in the field; past outcomes demonstrably do not affect future draws.
- **Methodology:** Empirical analysis of pari-mutuel betting pools after winning numbers.
- **Operational principle:** Use this as the empirical counter-evidence: even in real play, avoiding "recent" numbers has no benefit; cite it when explaining independence.
- **Applied in:** `references/cognitive-biases.md` §1–2; `references/combinatorics.md` (misconceptions preview).

### P7. Croson, R., & Sundali, J. (2005). The Gambler's Fallacy and the Hot Hand: Empirical Data from Casinos. *Journal of Risk and Uncertainty*.
- **Core finding:** Rapid-draw games intensify fallacious pattern-belief; players chase "streaks" across rapid independent events. Directly applicable to Keno's ~10-minute cadence.
- **Methodology:** Field observation of casino betting across rapid games.
- **Operational principle:** Flag rapid-draw frequency, not per-draw odds, as Keno's dominant harm driver; counter "streak" beliefs explicitly.
- **Applied in:** `references/keno-math.md` (independence + rapid-draw fallacy); `references/cognitive-biases.md` §7.

### P8. Cohen, J., & Hansel, C. (1956). *Risk and Gambling: The Study of Subjective Probability*. Longmans, Green.
- **Core finding:** Subjective probability systematically diverges from objective probability in gambling; people overweight personally salient outcomes.
- **Methodology:** Foundational behavioural experiments.
- **Operational principle:** Anchor every claim to objective probability; correct subjective over-weighting of "my numbers" by showing the true combinatorial odds.
- **Applied in:** `references/cognitive-biases.md` (general framing); `odds` route teaching tips.

---

## Methodology 3 — Expected value & house edge (VND)

### P9. Clotfelter, C., & Cook, P. (1989). *Selling Hope: State Lotteries in America*. Harvard University Press.
- **Core finding:** State lotteries are designed to return a fixed fraction (~50%) of sales; players systematically underestimate the house edge and overestimate win chances; lotteries are marketed on hope, not value.
- **Methodology:** Economic/behavioural analysis of state lottery structure and marketing.
- **Operational principle:** Always state the house edge and expected loss explicitly; frame spending as buying entertainment/hope, priced honestly.
- **Applied in:** `references/expected-value.md`; `config/skill-settings.json` guardrails (`always_mention_house_edge`, `always_frame_as_entertainment`).

### P10. Haigh, J. (1997). (Cross-listed with P2 — EV methodology.) See P2.

### P11. Forrest, D., Gulley, O., & Simmons, R. (2000). (Cross-listed with P3 — pari-mutuel EV.) See P3.

### P12. Rogers, P. (1998). The Cognitive Psychology of Lottery Gambling: A Theoretical Review. *Journal of Gambling Studies*, 14(4).
- **Core finding:** Lottery cognition is dominated by illusion of control and distorted perceived skill; "near-misses" and "small wins" sustain play despite negative EV; players conflate frequent small wins with being "ahead."
- **Methodology:** Theoretical review integrating cognitive psychology with lottery specifics.
- **Operational principle:** Pre-empt "small wins prove I'm ahead" by explaining that small wins are part of the designed EV; near-misses are statistically common, not predictive.
- **Applied in:** `references/cognitive-biases.md` §5–6 and the "small wins" misconception in `references/expected-value.md`; `ev` route responses.

### P13. Ariyabuddhiphongs, V. (2011). Lottery Gambling: A Review. *Journal of Gambling Studies*, 27(2).
- **Core finding:** Comprehensive review confirms: lottery players overestimate winning probability, superstitious number selection is widespread, and repeated small losses accumulate; educational interventions on probability/odds are the evidence-based counter.
- **Methodology:** Systematic literature review of lottery gambling studies.
- **Operational principle:** Treat the skill itself as the evidence-based educational intervention; target the documented distortions (overestimated probability, superstition, cumulative small losses).
- **Applied in:** Overall skill design rationale; `references/expected-value.md` long-term projection; `references/cognitive-biases.md`.

---

## Methodology 4 — Behavioural economics of gambling

### P14. Tversky, A., & Kahneman, D. (1974). Judgment under Uncertainty: Heuristics and Biases. *Science*, 185(4157).
- **Core finding:** Three heuristics (representativeness, availability, anchoring/adjustment) drive systematic probability errors; availability makes vivid jackpot winners seem common.
- **Methodology:** Foundational heuristics-and-biases program.
- **Operational principle:** Counter the availability heuristic explicitly: "we hear about every jackpot winner, never about the millions who lost."
- **Applied in:** `references/cognitive-biases.md` §6 (availability); `mythbust` route.

### P15. Langer, E., & Roth, J. (1975). Heads I Win, Tails It's Chance: The Illusion of Control. *Journal of Personality and Social Psychology*, 32(6).
- **Core finding:** People develop illusory control over purely chance tasks, amplified by familiarity/involvement; regular players build elaborate "systems" that don't work.
- **Methodology:** Chance-task experiments varying outcome sequence.
- **Operational principle:** Name "illusion of control" for prediction-method software, "soi cầu" systems, and ritualistic play; the machine is unaffected by player choice.
- **Applied in:** `references/cognitive-biases.md` §4; `tests/test_cases.md` A3, D4.

### P16. Wagenaar, W. (1988). *Paradoxes of Gambling Behaviour*. Erlbaum.
- **Core finding:** Comprehensive review of cognitive biases sustaining gambling (illusory control, interpretive bias, flexible attribution, "chase" rationalisations); gambling persists because losses are re-interpreted, not because EV is positive.
- **Methodology:** Review of cognitive research on gambling persistence.
- **Operational principle:** Recognise loss-chasing rationalisations; do not argue the user out of a feeling — provide transparent math and redirect to responsible play.
- **Applied in:** `references/cognitive-biases.md`; `risk_scan` keyword list and `responsible_play` route framing.

### P17. Griffiths, M. (1994). The Role of Cognitive Bias and Skill in Fruit Machine Gambling. *British Journal of Psychology*, 85(3).
- **Core finding:** Gamblers show systematic cognitive distortions (illusion of control, interpretive bias, predictive bias); near-misses activate win-like responses.
- **Methodology:** Empirical study of regular vs non-regular gamblers on fruit machines.
- **Operational principle:** Treat near-miss ("suýt trúng") framing as a distortion to correct, not a signal; explain near-miss statistical commonness.
- **Applied in:** `references/cognitive-biases.md` §5; `mythbust` route near-miss response.

### P18. Griffiths, M., & Wood, R. (2001). The Psychology of Lottery Gambling. *International Gambling Studies*, 1(1).
- **Core finding:** Lottery play is sustained by structural features (intermittent reinforcement, anticipation, near-misses) rather than positive EV; the "entertainment" of anticipation is the real product.
- **Methodology:** Empirical study of psychological factors in lottery play.
- **Operational principle:** Validate the legitimate entertainment value of anticipation while pricing it honestly; this is the bridge between "never invest" and "it's OK as budgeted fun."
- **Applied in:** `references/expected-value.md` entertainment framing; `references/responsible-gambling.md` budgeting; `config/skill-settings.json` `always_frame_as_entertainment`.

### P19. Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
- **Core finding:** Synthesis: System 1 (fast, intuitive, bias-prone) dominates gambling judgments; System 2 (slow, analytic) is engaged only when prompted; presenting transparent derivations recruits System 2.
- **Methodology:** Synthesis of decades of heuristics-and-biases research.
- **Operational principle:** Show step-by-step math to recruit System 2; don't just state conclusions — derivations are the intervention.
- **Applied in:** `config/feature-flags.json` `show_calculation_steps`; `quality_check` hook; all tool outputs include `calculation_steps`.

### P20. Wood, R., & Griffiths, M. (2002). Adolescent Perceptions of the National Lottery and Scratchcards. *Journal of Adolescence*, 25(1).
- **Core finding:** Young people hold measurable lottery-related cognitive distortions; public-education framing matters for harm reduction; age-of-play norms shape behaviour.
- **Methodology:** Qualitative group interviews with adolescents.
- **Operational principle:** Include age-considerate messaging; note the legal age (18+); emphasise that brain development (~25) raises impulsivity vulnerability.
- **Applied in:** `references/responsible-gambling.md` age-considerate messaging (young adults); `config/resources.json` regulatory context.

### P21. Rogers, P. (1998). (Cross-listed with P12 — lottery cognition.) See P12.

---

## Methodology 5 — Responsible gambling (Vietnam context)

### P22. Shaffer, H., Hall, M., & Vander Bilt, J. (1999). Estimating the Prevalence of Disordered Gambling Behavior in the United States and Canada. *American Journal of Public Health*, 89(9).
- **Core finding:** Disordered gambling has measurable population prevalence; risk factors are identifiable and screenable; the case for systematic screening is established.
- **Methodology:** Research synthesis/meta-analysis of prevalence studies.
- **Operational principle:** Justify educational screening (not diagnosis) as evidence-based; keep screening strictly informational with professional referral.
- **Applied in:** `references/responsible-gambling.md`; `scripts/risk_screener.py` (educational-only disclaimer).

### P23. Ladouceur, R., & Walker, M. (1996). A Cognitive Perspective on Gambling. In *Trends in Cognitive and Behavioural Therapies*.
- **Core finding:** Gambling is maintained by cognitive distortions; cognitive-behavioural correction of distorted beliefs is the established treatment framework.
- **Methodology:** CBT framework review.
- **Operational principle:** The skill's myth-busting is aligned with the CBT principle of cognitive correction; when risk is high, refer to CBT-qualified professionals.
- **Applied in:** `references/cognitive-biases.md` (debunking as cognitive correction); `references/responsible-gambling.md` (professional referral to CBT-qualified services).

### P24. Petry, N. (2005). *Pathological Gambling: Etiology, Comorbidity, and Treatment*. American Psychological Association.
- **Core finding:** Gambling disorder is a recognised clinical condition with effective treatments; comorbidity with mood/anxiety/substance conditions is common; brief interventions and referral work.
- **Methodology:** Clinical synthesis of pathological gambling research.
- **Operational principle:** Frame gambling difficulties as a recognised, treatable health condition (not a moral failing); emphasise that effective treatment exists; refer, don't treat.
- **Applied in:** `references/responsible-gambling.md` (no-judgment framing, "effective treatment" language); `config/resources.json` professional_consultation framing.

### P25. Ferris, J., & Wynne, H. (2001). *The Canadian Problem Gambling Index (PGSI)*. Canadian Centre on Substance Abuse.
- **Core finding:** The PGSI is a validated 9-item population-screening instrument with established cut-points (0 non-problem; 1–2 low; 3–7 moderate; 8+ problem).
- **Methodology:** Instrument development and validation.
- **Operational principle:** Implement PGSI scoring faithfully with its validated thresholds; never repurpose it as diagnosis.
- **Applied in:** `scripts/risk_screener.py` `screen_pgsi` (exact thresholds); `screen_risk` tool output schema.

### P26. National Council on Problem Gambling (NCPG) (2021). *Problem Gambling Screening and Brief Intervention Toolkit*.
- **Core finding:** Brief screens (NCPG Lie/Bet-style items) plus brief intervention + referral are an effective, low-cost pathway; helplines reduce harm.
- **Methodology:** Toolkit synthesis of screening + brief intervention evidence.
- **Operational principle:** Implement the NCPG-style brief screen; on positive screens, deliver a brief non-judgmental intervention (normalise + offer resources) and refer.
- **Applied in:** `scripts/risk_screener.py` `screen_ncpg`; `responsible_play` route intervention framework.

### P27. Raylu, N., & Oei, T. (2004). Role of Culture in Gambling and Problem Gambling: An Acculturation Study. *Journal of Gambling Studies*, 20(1).
- **Core finding:** Culture shapes gambling cognition, superstitious belief, and help-seeking; in Asian populations, culturally-specific beliefs (luck, fate, numerology) and lower help-seeking make culturally-adapted education and resources essential.
- **Methodology:** Acculturation study of Asian-background gamblers.
- **Operational principle:** Adapt all messaging to the Vietnamese cultural context (so dep, ngay sinh, phong thuy-style numerology); use non-stigmatising language; provide culturally accessible entry points (mental-health/medical/social rather than Western-style "counselling" alone).
- **Applied in:** `references/cognitive-biases.md` (Vietnamese-context myths); `references/responsible-gambling.md` (Vietnam resources + non-judgment framing); `config/resources.json`.

### P28. Delfabbro, P., & King, D. (2012). Gambling and Problem Gambling in Australia. In *Community Psychology and Positive Psychology*.
- **Core finding:** Population-level responsible-gambling guidelines (budget limits, no-chase rules, entertainment framing) reduce harm; harm-minimisation is more effective than abstinence-only messaging for the broad player base.
- **Methodology:** Applied review of responsible-gambling strategy.
- **Operational principle:** Lead with harm-minimisation (budget, no-chase, entertainment framing) rather than only "don't gamble"; give practical, actionable limits.
- **Applied in:** `references/responsible-gambling.md` budgeting & no-chase guidelines; `config/skill-settings.json` `always_frame_as_entertainment`.

### P29. Ministry of Finance of Vietnam (2007). Decree No. 30/2007/ND-CP (and amendments) on Lottery Business.
- **Core finding:** Establishes Vietlott's legal operating framework, age of play (18+), and the state-licensed monopoly context — the regulatory ground truth for responsible-play messaging.
- **Methodology:** Regulatory statute.
- **Operational principle:** Ground responsible-play context in the actual Vietnamese regulatory framework; state the legal age and operator status.
- **Applied in:** `references/responsible-gambling.md` regulatory context; `config/resources.json` regulatory_context.

### P30. Vietlott (Vietnam Lottery Company). Prize Structure and Game Rules for Mega 6/45, Power 6/55, Keno, and Max 3D (official documentation, updated periodically).
- **Core finding:** The authoritative source for game structure, prize amounts, and draw mechanics; pari-mutuel tiers vary draw-to-draw; prize amounts must be verified at source.
- **Methodology:** Operator-published rules.
- **Operational principle:** Derive odds from the documented draw mechanics; treat prize *amounts* as representative and always direct users to verify current official figures at vietlott.vn; never present a single EV figure as permanent truth.
- **Applied in:** `config/games.json` (representative prizes + verify note); `scripts/seed_games.py` (mechanism-based derivation); every reference file's prize caveat.

---

## Research-to-Skill Application Matrix

| # | Paper (short) | Methodology | Skill component applying it |
|---|---------------|-------------|-----------------------------|
| P1 | Feller 1968 | Combinatorial odds | `references/combinatorics.md`; `scripts/combinatorics.py`; `calculate_odds` |
| P2 | Haigh 1997 | EV / "1 in N" | `references/expected-value.md`; `scripts/expected_value.py`; odds format flag |
| P3 | Forrest/Gulley/Simmons 2000 | Pari-mutuel EV | `references/expected-value.md`; `references/cognitive-biases.md` §4 |
| P4 | Tversky & Kahneman 1971 | Law of small numbers | `references/cognitive-biases.md` §1–3; `mythbust` route |
| P5 | Kahneman & Tversky 1972 | Representativeness | `references/cognitive-biases.md` §3 |
| P6 | Clotfelter & Cook 1993 | Gambler's fallacy (field) | `references/cognitive-biases.md` §1–2 |
| P7 | Croson & Sundali 2005 | Rapid-draw fallacy | `references/keno-math.md`; `references/cognitive-biases.md` §7 |
| P8 | Cohen & Hansel 1956 | Subjective probability | `references/cognitive-biases.md` framing |
| P9 | Clotfelter & Cook 1989 | House edge framing | `references/expected-value.md`; guardrail `always_mention_house_edge` |
| P12 | Rogers 1998 | Lottery cognition | `references/cognitive-biases.md` §5–6; `ev` route |
| P13 | Ariyabuddhiphongs 2011 | Lottery review | Overall skill design; long-term projection |
| P14 | Tversky & Kahneman 1974 | Availability heuristic | `references/cognitive-biases.md` §6 |
| P15 | Langer & Roth 1975 | Illusion of control | `references/cognitive-biases.md` §4; `tests` A3, D4 |
| P16 | Wagenaar 1988 | Loss-chase rationalisation | `references/cognitive-biases.md`; risk keywords |
| P17 | Griffiths 1994 | Near-miss distortion | `references/cognitive-biases.md` §5 |
| P18 | Griffiths & Wood 2001 | Anticipation as product | `references/expected-value.md` entertainment; `responsible-gambling.md` |
| P19 | Kahneman 2011 | System 1 vs System 2 | `show_calculation_steps`; `quality_check`; all tool outputs |
| P20 | Wood & Griffiths 2002 | Adolescent framing | `responsible-gambling.md` age messaging; legal age |
| P22 | Shaffer et al. 1999 | Screening justification | `responsible-gambling.md`; `risk_screener.py` |
| P23 | Ladouceur & Walker 1996 | CBT cognitive correction | `cognitive-biases.md` debunking; professional referral |
| P24 | Petry 2005 | Gambling disorder clinical | `responsible-gambling.md` no-judgment framing |
| P25 | Ferris & Wynne 2001 | PGSI thresholds | `scripts/risk_screener.py screen_pgsi` |
| P26 | NCPG 2021 | Brief screen + intervention | `scripts/risk_screener.py screen_ncpg`; `responsible_play` route |
| P27 | Raylu & Oei 2004 | Culture/adaptation | Vietnamese-context myths + resources |
| P28 | Delfabbro & King 2012 | Harm-minimisation | `responsible-gambling.md` budgeting/no-chase |
| P29 | Decree 30/2007/ND-CP | Regulatory context | `responsible-gambling.md`; `resources.json` |
| P30 | Vietlott rules | Game structure source | `config/games.json`; `scripts/seed_games.py` |

---

## How to use this brain

1. **When building a `mythbust` answer:** open the relevant entries (P4–P8, P14–P17) and cite the specific finding behind each correction ("Tversky & Kahneman 1971 showed people expect small samples to look balanced…").
2. **When building an `ev` answer:** cite P2/P9/P12/P13 and show the per-tier derivation (P19: recruit System 2).
3. **When routing to `responsible_play`:** draw framing from P22–P28 — screening is educational (P22), gambling disorder is treatable (P24), culture matters (P27), harm-minimisation beats abstinence-only (P28).
4. **When the `quality_check` hook runs:** verify the answer cites at least one paper from the relevant methodology group above; if not, strengthen the grounding.
5. **On any uncertainty about a prize figure:** defer to P30 — verify at vietlott.vn; never assert a permanent EV.

## Updating this brain

Add new sources by appending an entry under the matching methodology with all five fields (Citation / Core finding / Methodology / Operational principle / Applied in) and a row in the matrix. Keep `SECOND-BRAIN-KNOWLEDGE-PAPER.md` as the flat reading list; keep this file as the operational, mapped brain.
