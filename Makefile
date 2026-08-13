# Makefile for the Vietlott Statistics & Responsible-Play Advisor
# Windows-friendly: uses `python` (ensure python is on PATH). For POSIX, set PYTHON=python3.

PYTHON ?= python
PYTEST := $(PYTHON) -m pytest

.PHONY: help validate seed calculators tests ci clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-12s %s\n", $$1, $$2}'

validate: ## Validate all config (schema + parse)
	$(PYTHON) scripts/validate_config.py
	$(PYTHON) scripts/config_loader.py

seed: ## Regenerate config/games.json from first-principles calculators
	$(PYTHON) scripts/seed_games.py

ingest: ## Ingest draw results (synthetic fixture by default; real data via config/ingestion.json)
	$(PYTHON) scripts/ingest_results.py

independence: ## Run statistical independence tests on ingested draw data
	$(PYTHON) scripts/independence_test.py

calculators: ## Run every calculator/demo script
	$(PYTHON) scripts/combinatorics.py
	$(PYTHON) scripts/keno_calculator.py
	$(PYTHON) scripts/max3d_calculator.py
	$(PYTHON) scripts/expected_value.py
	$(PYTHON) scripts/wheeling_analyzer.py
	$(PYTHON) scripts/risk_screener.py

tests: ## Run the pytest suite
	$(PYTEST) tests/ -q --no-header

ci: validate seed ingest independence calculators tests ## Full end-to-end CI verification (or: python scripts/run_all.py)
	@echo "CI: all steps passed"

clean: ## Remove build artifacts
	-@del /Q scripts\__pycache__ 2>nul
	-@rmdir /Q scripts\__pycache__ 2>nul
	-@del /Q tests\__pycache__ 2>nul
	-@rmdir /Q tests\__pycache__ 2>nul
	-@del /Q .pytest_cache 2>nul
