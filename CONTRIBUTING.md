# Contributing to the Vietlott Statistics & Responsible-Play Advisor

Thank you for your interest in improving this educational skill. This document explains how to make changes safely.

## Project constraints (read first)

- **Hard guardrail:** this skill never generates "predicted winning numbers". Any change that weakens this guardrail will not be accepted.
- **Computed, not hand-typed, odds.** Never edit probabilities/odds directly in `config/games.json`. Edit prize assumptions in `scripts/seed_games.py` (or the calculator modules) and re-run `python scripts/seed_games.py` to regenerate.
- **Educational only.** Risk screening is screening, not diagnosis. Any change that presents screening as diagnosis or treatment will not be accepted.

## Development workflow

```powershell
# 1. Validate configuration
python scripts/validate_config.py
python scripts/config_loader.py

# 2. (If you changed prize assumptions) regenerate games.json
python scripts/seed_games.py

# 3. Run the full CI harness (validates, regenerates, runs all calculators, runs tests)
python scripts/run_all.py
#    or: make ci
```

The CI harness must pass (10/10 steps) before a change is considered ready.

## How to add things

- **A new Vietlott game / prize change:** add prize assumptions to `scripts/seed_games.py` (or a new calculator module), re-run the seeder, add reference coverage in `references/`, add test assertions in `tests/test_vietlott.py`.
- **A new tool:** define its JSON input/output schema in `SKILL.md`, add an executable handler in `scripts/`, register it in the sub-advisor registry table and `assets/system-architecture.md`, add pytest coverage.
- **A new region's resources:** edit `config/resources.json`.
- **A new bias/explainer:** edit `references/cognitive-biases.md` and add a research entry to `RESEARCH-PAPER-KNOWLEDGE-BRAIN.md` (Citation / Core finding / Methodology / Operational principle / Applied in) plus a row in the application matrix.
- **A new feature flag:** add it to `config/feature-flags.json:feature_flags` and to `config/feature-flags.schema.json` (keep the schema in sync), then expose it via `scripts/config_loader.py` if needed.

## Testing expectations

- Add or extend `tests/test_vietlott.py` for any new numeric claim or behaviour.
- Keno distributions must sum to 1.0 (`keno_calculator.validate_distribution`); all EVs must be negative; all odds > 1.
- Keep the suite fast (currently <1s).

## Research sourcing

When adding a research claim, prefer a source already in `RESEARCH-PAPER-KNOWLEDGE-BRAIN.md` or `SECOND-BRAIN-KNOWLEDGE-PAPER.md`. Flag any unsourced claim explicitly. Verify any specific citation's title/year/venue independently before relying on it in a formal deliverable.

## Code style

- Python 3.9+; type hints; dataclasses; module docstrings; `from __future__ import annotations`.
- Import-safe modules (no side effects on import); CLI via `if __name__ == "__main__": main()`.
- UTF-8 without BOM for all files; scripts read config with `utf-8-sig` (BOM-tolerant).

## Reporting issues

When reporting an issue, include the output of `python scripts/run_all.py` and the specific route/tool involved.
