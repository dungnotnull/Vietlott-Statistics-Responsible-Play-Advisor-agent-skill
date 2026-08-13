# System Architecture — Vietlott Statistics & Responsible-Play Advisor

## Overview

A modular Claude Skill with a **chain-of-thought skill-router** that classifies
user intent and dispatches to one of five specialized **sub-advisor** skills.
Each sub-advisor owns a reference file and one or more **tools** (JSON-schema
inputs, executable Python handlers in `scripts/`). **Hooks** run before and
after each routed turn to enforce guardrails, inject the disclaimer, scan for
risk language, and emit structured logs. A **skill registry** documents
registration, resolution, execution, and validation.

```
                        +-----------------------------+
   user query  ------>   |   Pre-processing hooks      |
                        |  intent_detect | risk_scan  |
                        |  guardrail_check | log       |
                        +---------------+-------------+
                                        |
                                        v
                        +-----------------------------+
                        |   Skill router (CoT)        |
                        |  classify intent -> route    |
                        +---------------+-------------+
                                        |
          +-------------+-------------+-------------+-------------+-------------+
          v             v             v             v             v             v
   odds-advisor  ev-advisor  mythbuster-  keno/max3d-  responsible-  prediction_
                                       advisor       advisor       play-advisor  refusal(fallback)
          |             |             |             |             |
          v             v             v             v             v
   tools:          tools:        ref:          tools:        tools:
   calculate_odds   calc_ev       cognitive-    keno_calc     screen_risk
   (combinatorics)  (expected_    biases.md     max3d_calc    (risk_screener)
                    value.py)     wheeling.md
                                        |
                                        v
                        +-----------------------------+
                        |   Post-processing hooks     |
                        |  disclaimer_inject          |
                        |  resource_attach (if risk)  |
                        |  quality_check | log        |
                        +-----------------------------+
                                        |
                                        v
                                    response (+ disclaimer)
```

## Sub-advisor registry

| Sub-advisor | Owns reference | Tools | Route label | Trigger (examples) |
|-------------|----------------|-------|-------------|--------------------|
| vietlott-odds-advisor | references/combinatorics.md | calculate_odds | odds | "ti le Mega 6/45", "xac suat Power 6/55 jackpot" |
| vietlott-ev-advisor | references/expected-value.md | calculate_expected_value, long_term_projection | ev | "ky vong Mega", "house edge Keno", "mat bao nhieu 1 nam" |
| vietlott-mythbuster-advisor | references/cognitive-biases.md, references/wheeling-systems.md | analyze_wheeling_system | mythbust | "so hot/cold", "soi cau", "phuong phap du doan", "wheeling" |
| vietlott-keno-max3d-advisor | references/keno-math.md, references/max3d-math.md | calculate_keno_odds, calculate_max3d_ev | keno_max3d | "Keno chon 7", "Max 3D co de trung khong", "Keno quay nhanh" |
| vietlott-responsibleplay-advisor | references/responsible-gambling.md | screen_risk | responsible_play | "gỡ lại", "khong the dung choi", "muon vay tien choi", risk keywords |

## Tool schemas (summary; full JSON in SKILL.md)

- `calculate_odds` — `{game, pool_size, numbers_drawn, match_requirement}` -> `{odds_1_in, probability, calculation}`
- `calculate_expected_value` — `{game, keno_select?, max3d_mode?}` -> `{expected_value_vnd, house_edge_percent, steps}`
- `calculate_keno_odds` — `{select, match}` -> `{probability, odds_1_in}`
- `calculate_max3d_ev` — `{mode}` -> `{expected_value_vnd, house_edge_percent, tiers}`
- `analyze_wheeling_system` — `{chosen_count, guarantee_match, ticket_count, pool_size}` -> `{coverage, cost_factor, what_it_does, what_it_does_not_do}`
- `screen_risk` — `{framework, responses}` -> `{risk_level, recommendation, indicators, resources}`

## Hooks

### Pre-processing
- `intent_detect` — classify into route labels; default `odds`; escalate `responsible_play` on risk.
- `risk_scan` — diacritic-insensitive VI+EN keyword heuristic (`scripts/risk_screener.py detect_risk_in_text`); threshold from `config/skill-settings.json`.
- `guardrail_check` — hard refuse prediction requests (no `never_generate_predictions` violation).
- `log` — structured log entry (intent, route, game, tokens).

### Post-processing
- `disclaimer_inject` — append standing disclaimer (VI+EN) to every substantive response.
- `resource_attach` — if risk flagged, attach Vietnam resources from `config/resources.json`.
- `quality_check` — verify research grounding, transparent math, no prediction endorsement.
- `log` — close log entry (disclaimer_emitted, risk_flagged, fallback_triggered).

## Configuration & state

- **Stateless** by design (privacy-first): no persistent user state; session-level game-parameter memory only.
- **Config** loaded via `scripts/config_loader.py` from `config/`:
  - `feature-flags.json` (+ `feature-flags.schema.json`) — env, LLM params, feature flags, guardrails.
  - `games.json` — Vietlott game structures (regenerated by `scripts/seed_games.py`).
  - `resources.json` — Vietnam + international support resources.
  - `skill-settings.json` — behavior, router, risk detection, formatting.
- **Env overrides** described in `feature-flags.json:env_variables` (`VIETLOTT_*`).

## Error handling & fallbacks

- LLM/computation failure -> graceful fallback message (from `config/skill-settings.json:error_handling.fallback_message`) offering the general framework + a worked example instead of failing silently.
- Ambiguous input -> state assumptions explicitly; offer adjustment.
- Missing data -> request specifics; provide example with representative values; offer to proceed with assumptions.
- Calculation errors -> state error clearly; never fabricate numbers; offer alternative approach.

## Context-window optimization

- Start with a high-level answer (2-3 sentences).
- Offer detail on request (progressive disclosure; `config/feature-flags.json:llm.progressive_disclosure`).
- Load only the specific reference file needed (`selective_reference_loading`).
- Context budget: `config/feature-flags.json:llm.context_budget_tokens` (default 8000).

## Quality gates (every response)

Must: include disclaimer; ground in research; show transparent math; use VND + Vietnamese context; flag professional referral when warranted.
Must not: generate predictions; suggest beating house edge; frame as investment/income; guarantee wins; encourage increased spending; diagnose/treat.

## Extension points

- Add games by editing `scripts/seed_games.py` prize assumptions and re-running `python scripts/seed_games.py`.
- Add regions by editing `config/resources.json`.
- Add biases/explainers in `references/`.
- Add tools by defining a JSON schema in SKILL.md and a Python handler in `scripts/`.
