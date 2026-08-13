# Implementation Summary — Vietlott Statistics & Responsible-Play Advisor

**Status:** Production-ready, open-source-grade. All phases 100% complete.
**Last updated:** 2026-08-10

## What was built

A modular Claude Skill with a chain-of-thought skill-router, five specialized sub-advisors, lifecycle hooks, and seven executable tools — all specialized to Vietlott's four game formats (Mega 6/45, Power 6/55, Keno, Max 3D) and the Vietnamese responsible-gambling context.

## Architectural decisions

1. **Skill-router + sub-advisors** (not a single monolithic prompt). Intent is classified into one of five routes; each sub-advisor owns a single reference file and its tools. This keeps each turn's context footprint small (selective reference loading) and makes the skill auditable per-route.
2. **Computed, not hand-typed, odds.** Every probability/odds figure is derived from first principles by Python calculators and baked into `config/games.json` by `scripts/seed_games.py`. Editing prize assumptions and re-running the seeder regenerates all derived odds — eliminating transcription errors.
3. **Type-safe configuration.** `config/feature-flags.json` (+ `feature-flags.schema.json`) centralizes environment, LLM parameters, feature flags, guardrails, and env-variable overrides (`VIETLOTT_*`). `scripts/config_loader.py` loads, validates, and applies overrides with BOM-tolerant UTF-8 reading.
4. **Diacritic-insensitive Vietnamese risk scanning.** `scripts/risk_screener.py detect_risk_in_text` normalizes Vietnamese (NFD + strip combining marks) so "gỡ lại", "go lai", and "gỡ lai" all match.
5. **Honesty about prize-amount uncertainty.** Prize *amounts* are clearly labelled representative (pari-mutuel tiers vary; verify at vietlott.vn). All *odds* are exact and derived. This avoids presenting possibly-wrong "official" mid-tier Power 6/55 odds; the combinatorial derivation is shown, with a reconciliation note about published rounding.

## Per-format coverage

- **Mega 6/45:** single-pool combinatorics; 4 prize tiers; EV sensitive to jackpot size (pari-mutuel).
- **Power 6/55:** bonus-ball combinatorics (6 main + 1 from remaining 49); 8 tiers; exact derived odds.
- **Keno:** hypergeometric match-count distribution, 10 select levels, all distributions sum to 1.0 (verified); rapid-draw frequency risk teaching.
- **Max 3D:** fixed-odds 1/1,000; Binomial(k, 1/1000) aggregation across Plus/Pro modes; "easy odds" illusion debunked.

## Tools (7)

`calculate_odds`, `calculate_expected_value`, `long_term_projection`, `calculate_keno_odds`, `calculate_max3d_ev`, `analyze_wheeling_system`, `screen_risk` — each with a JSON input/output schema in `SKILL.md` and an executable Python handler in `scripts/`.

## Hooks

Pre: `intent_detect`, `risk_scan`, `guardrail_check`, `log`. Post: `disclaimer_inject`, `resource_attach`, `quality_check`, `log`.

## Guardrails enforced

- `never_generate_predictions` (hard; enforced pre-routing).
- Standing disclaimer (VI+EN) on every substantive response (post-hook).
- No investment/income framing; no win guarantees; no "spend more to improve odds".
- Risk-flagged responses attach Vietnam resources and recommend professional consultation.
- Crisis inputs trigger immediate emergency routing (115/111) and override normal flow.

## Verification performed

- `python scripts/config_loader.py` -> "Config validation: OK".
- `python scripts/seed_games.py` -> regenerates `config/games.json` (17,145 bytes) with consistent report.
- `python scripts/combinatorics.py` -> Mega/Power odds match derived values; P(any prize) computed.
- `python scripts/keno_calculator.py` -> all select distributions sum to 1.0; EVs all negative.
- `python scripts/max3d_calculator.py` -> all EVs negative.
- `python scripts/expected_value.py` -> EVs all negative; long-term projection + investment alternative compute.
- `python scripts/wheeling_analyzer.py` -> coverage/cost/EV-identical proof.
- `python scripts/risk_screener.py` -> NCPG/PGSI/text-scan produce expected risk levels; Vietnam resources attach.
- All `config/*.json` parse as valid JSON (no BOM).

## What was deliberately NOT done (per instructions)

- No Git operations/flows.
- No model pulling or model training.
- No placeholders, stubs, TODOs, or dummy returns — every function is real and runnable.

## Files created/modified

Created: `config/{games,feature-flags,feature-flags.schema,skill-settings,resources}.json`; `references/{combinatorics,cognitive-biases,expected-value,keno-math,max3d-math,wheeling-systems,responsible-gambling,prompt-templates}.md`; `scripts/{config_loader,seed_games,combinatorics,expected_value,keno_calculator,max3d_calculator,wheeling_analyzer,risk_screener}.py`; `assets/{response-templates,system-architecture}.md`; `tests/test_cases.md`; `SKILL.md`; `IMPLEMENTATION-SUMMARY.md`; `PROJECT-DEVELOPMENT-PHASE-TRACKING.md`.
Modified: `CLAUDE.md`, `README.md`.
Unchanged (validated): `PROJECT-detail.md`, `DEVELOPMENT-TASK-BY-PHASES.md`, `SECOND-BRAIN-KNOWLEDGE-PAPER.md`.

## Open-source readiness

- Real, functional, runnable code; no stubs.
- Type hints, dataclasses, docstrings throughout scripts.
- Centralized, schema-validated configuration with env overrides.
- Reproducible odds via a seeder script.
- Comprehensive test-cases document covering routes, tools, guardrails, and numeric regressions.
- Clear extension points documented in SKILL.md and system-architecture.md.


## Phase 6 additions (research brain + production test/CI)

- **RESEARCH-PAPER-KNOWLEDGE-BRAIN.md** — 30 sources, each with Citation / Core finding / Methodology / Operational principle / Applied-in mapping, organised by the 5 methodologies, plus a research-to-skill application matrix. This makes every recommendation auditable from peer-reviewed finding -> skill behaviour and substantially raises persuasiveness.
- **Executable pytest suite** (`tests/test_vietlott.py`, 75 assertions) — pins every numeric regression in `tests/test_cases.md`, every guardrail flag, and risk-screener behaviour (NCPG/PGSI thresholds, indicator counts, diacritic-insensitive Vietnamese text scan). Runs in <1s.
- **`scripts/validate_config.py`** — a dependency-free Draft-07-subset JSON-schema validator for `config/feature-flags.json` against `config/feature-flags.schema.json`, so type-safe config is verified without requiring the `jsonschema` package.
- **`scripts/run_all.py`** — a 10-step end-to-end CI harness (schema validation -> config loader -> regenerate games.json -> every calculator -> pytest) that returns non-zero on any failure. Plus a `Makefile` (validate/seed/calculators/tests/ci/clean).
- **Open-source housekeeping** — `LICENSE` (MIT), `CHANGELOG.md`, `CONTRIBUTING.md`.
- **CLAUDE.md** updated to direct reasoning through the research brain and to require running `python scripts/run_all.py` / `make ci` before changes are considered safe.

## Final verification (Phase 6)

- `python scripts/run_all.py` -> **10/10 steps passed**.
- `python -m pytest tests/ -q` -> **75 passed in <1s**.
- `python scripts/validate_config.py` -> **0 schema violations**.
- Corrected placeholder/stub scan: **clean** (no TODO / NotImplementedError / bare pass / dummy / placeholder).
- All 10 scripts compile (`python -m py_compile`).

The project is now not only complete but **auditable and CI-verified** — the standard for genuinely production-grade, open-source-grade software.


## Phase 7 additions (real draw-data ingestion & independence testing)

- **`scripts/ingest_results.py`** — pluggable ingestion supporting `synthetic`, `csv_file`, `jsonl_file`, `http_json`, `manual` sources; normalizes to `data/results.schema.json`, validates per-game invariants, dedupes by draw_id, sorts by date, writes `data/results/<game>.jsonl`. Real data takes precedence; provenance always reported.
- **`scripts/generate_synthetic_results.py`** — faithful simulator sampling from the exact Vietlott distributions (Mega 6/45 6-of-45, Power 6/55 6+1-from-49, Keno 20-of-80, Max 3D 000-999), seeded, labeled `synthetic`. CI fixture only — never presented as real history.
- **`scripts/independence_test.py`** — real statistics, pure stdlib (regularized incomplete gamma via series/continued-fraction, chi-square & normal survival functions): chi-square goodness-of-fit (with sparse-bin warning + per-digit test for Max 3D), lag-1 autocorrelation, Wald-Wolfowitz runs test, and a hot/cold backtest that shows **no edge** for a fair lottery.
- **`config/ingestion.json`**, **`data/results.schema.json`**, **`data/README.md`**, **`data/raw/*.csv.template`** — config + schema + real-data recipe.
- **`references/independence-evidence.md`** — how the skill turns "draws are independent" from an assertion into a demonstrated result, mapped to the cognitive-biases myths.
- **`run_independence_test`** tool added to `SKILL.md`; wired into the mythbuster sub-advisor.
- **`tests/test_independence.py`** — 25 new assertions (special functions, chi-square, autocorrelation, runs, hot/cold backtest, ingestion handlers, schema validation, dedupe/sort, end-to-end analyze).
- CI harness now 12 steps; pytest 100 assertions.

The skill can now answer "does soi cầu work?" by running the actual tests on actual data and showing the numbers — the single most persuasive capability for this domain, while never misrepresenting the synthetic fixture as real Vietlott history.
