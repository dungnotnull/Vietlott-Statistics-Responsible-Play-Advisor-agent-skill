"""Pytest configuration: make `scripts/` importable without PYTHONPATH tricks.

Adds the repository `scripts/` directory to sys.path so test modules can
`import combinatorics`, `import expected_value`, etc., directly. This keeps
the test suite self-contained for CI runners.
"""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
