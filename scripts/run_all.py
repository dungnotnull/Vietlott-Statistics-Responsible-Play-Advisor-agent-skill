#!/usr/bin/env python3
"""
End-to-end CI verification harness for the Vietlott skill.

Runs, in order:
  1. config schema validation       (scripts/validate_config.py)
  2. config loader validation      (scripts/config_loader.py)
  3. games.json regeneration        (scripts/seed_games.py)
  4. every calculator/demo script   (scripts/*.py except helpers)
  5. the pytest suite               (tests/test_vietlott.py)

Reports per-step pass/fail and a final summary. Exit code 0 only if all pass.

Usage:
    python scripts/run_all.py
    python scripts/run_all.py --no-tests   # skip pytest (e.g. if pytest absent)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
TESTS = ROOT / "tests"

# Scripts whose main() demonstrates a tool / produces output.
CALC_SCRIPTS = [
    "combinatorics.py",
    "keno_calculator.py",
    "max3d_calculator.py",
    "expected_value.py",
    "wheeling_analyzer.py",
    "risk_screener.py",
]
HELPER_SCRIPTS = ["validate_config.py", "config_loader.py", "seed_games.py"]


def _run(cmd: list[str], label: str, env: dict[str, str] | None = None) -> bool:
    print(f"\n=== {label} ===")
    print("$ " + " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=False)
    ok = proc.returncode == 0
    print(f"[{'PASS' if ok else 'FAIL'}] {label}")
    return ok


def main() -> int:
    import os
    base_env = dict(os.environ)
    base_env["PYTHONIOENCODING"] = "utf-8"
    base_env["PYTHONPATH"] = str(SCRIPTS)

    run_tests = "--no-tests" not in sys.argv

    results: list[tuple[str, bool]] = []

    results.append(("config schema validation", _run([sys.executable, "scripts/validate_config.py"], "config schema validation", base_env)))
    results.append(("config loader", _run([sys.executable, "scripts/config_loader.py"], "config loader", base_env)))
    results.append(("seed games.json", _run([sys.executable, "scripts/seed_games.py"], "regenerate games.json", base_env)))
    results.append(("ingest draw data", _run([sys.executable, "scripts/ingest_results.py"], "ingest draw results (synthetic fixture)", base_env)))
    results.append(("independence test", _run([sys.executable, "scripts/independence_test.py"], "statistical independence tests", base_env)))

    for s in CALC_SCRIPTS:
        results.append((s, _run([sys.executable, f"scripts/{s}"], s, base_env)))

    if run_tests:
        results.append(("pytest suite", _run([sys.executable, "-m", "pytest", "tests/", "-q", "--no-header"], "pytest suite", base_env)))

    print("\n" + "=" * 60)
    print("CI SUMMARY")
    print("=" * 60)
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"\n{passed}/{total} steps passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
