# Changelog

All notable changes to the Vietlott Statistics & Responsible-Play Advisor.

The format is based on Keep a Changelog, and this project adheres to
Semantic Versioning for the skill configuration (`config/feature-flags.json:version`).

## [1.1.0] — 2026-08-10

### Added
- Real draw-data ingestion framework: `scripts/ingest_results.py` with pluggable sources (synthetic, csv_file, jsonl_file, http_json, manual); `config/ingestion.json`; `data/results.schema.json`; `data/README.md`; `data/raw/*.csv.template`.
- `scripts/generate_synthetic_results.py` — faithful synthetic fixture generator (exact Vietlott distributions, seeded, labeled `synthetic`).
- `scripts/independence_test.py` — real statistical independence tests (chi-square goodness-of-fit, lag-1 autocorrelation, Wald-Wolfowitz runs test, hot/cold backtest) implemented from scratch with no third-party deps.
- `references/independence-evidence.md` — turning "draws are independent" from assertion to demonstrated result.
- `run_independence_test` tool schema in `SKILL.md`; wired into the mythbuster sub-advisor.
- `tests/test_independence.py` — 25 new assertions; total pytest suite now 100 assertions.
- CI harness now 12 steps (`make ci` / `python scripts/run_all.py`); new Makefile targets `ingest` and `independence`.

### Notes
- The official `vietlott.vn` site renders results via an AjaxPro handler requiring session/anti-forgery tokens, so it is intentionally NOT a default automated source; the CSV path is the reliable real-data ingestion route.
- Synthetic fixture is never presented as real Vietlott history; every report echoes provenance.

## [1.0.0] — 2026-08-10

### Added
- Modular Claude Skill with a chain-of-thought skill-router and five specialized sub-advisors (odds, ev, mythbuster, keno/max3d, responsible-play).
- Pre/post-processing hooks: intent_detect, risk_scan, guardrail_check, log; disclaimer_inject, resource_attach, quality_check, log.
- Seven executable tools with JSON input/output schemas and Python handlers: `calculate_odds`, `calculate_expected_value`, `long_term_projection`, `calculate_keno_odds`, `calculate_max3d_ev`, `analyze_wheeling_system`, `screen_risk`.
- Type-safe configuration: `config/feature-flags.json` (+ JSON schema), `games.json`, `skill-settings.json`, `resources.json`, loaded/validated by `scripts/config_loader.py` with env-variable overrides.
- First-principles odds calculators: `combinatorics.py` (single-pool + bonus-ball), `keno_calculator.py` (hypergeometric), `max3d_calculator.py` (fixed-odds binomial), `expected_value.py` (EV + long-term projection), `wheeling_analyzer.py`, `risk_screener.py` (NCPG/PGSI/indicators/diacritic-insensitive text scan).
- `scripts/seed_games.py` regenerates `config/games.json` from the calculators — all probabilities/odds are computed, never hand-typed.
- `scripts/validate_config.py` self-contained JSON-schema validator (no third-party deps).
- `scripts/run_all.py` end-to-end CI verification harness; `Makefile` with validate/seed/calculators/tests/ci targets.
- Executable pytest suite (`tests/test_vietlott.py`, `tests/conftest.py`) — 75 assertions across numeric regressions, guardrails, and risk-screener behaviour.
- Reference files: `combinatorics.md`, `cognitive-biases.md`, `expected-value.md`, `keno-math.md`, `max3d-math.md`, `wheeling-systems.md`, `responsible-gambling.md`, `prompt-templates.md`.
- `assets/system-architecture.md`, `assets/response-templates.md`.
- `RESEARCH-PAPER-KNOWLEDGE-BRAIN.md` — 30-source applied research brain with operational principles and a research-to-skill application matrix.
- `SECOND-BRAIN-KNOWLEDGE-PAPER.md` (curated reading list), `IMPLEMENTATION-SUMMARY.md`, `PROJECT-DEVELOPMENT-PHASE-TRACKING.md`.
- LICENSE (MIT), CONTRIBUTING.md.

### Guardrails
- Hard refusal of "predicted winning numbers"; standing VI/EN disclaimer on every substantive response; no investment/income framing; risk-flagged responses attach Vietnam resources and recommend professional consultation; crisis inputs route to 115/111.

### Notes
- Prize *amounts* are representative (pari-mutuel tiers vary; verify at https://vietlott.vn). All *odds* are combinatorially derived. Power 6/55 mid-tier odds are derived from the 6+1-from-49 mechanism with a reconciliation note about published rounding.
