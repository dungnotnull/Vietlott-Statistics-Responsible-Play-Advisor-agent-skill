#!/usr/bin/env python3
"""
Type-safe configuration loader for the Vietlott skill.

Loads and validates config/*.json, applying environment-variable overrides and
feature flags. Used by every script so configuration is centralized and
consistent. Reads files with utf-8-sig to be BOM-tolerant on Windows.

Public API:
    load_settings()    -> dict   (config/skill-settings.json + env overrides)
    load_games()        -> dict   (config/games.json)
    load_resources()    -> dict   (config/resources.json)
    load_feature_flags()-> dict  (config/feature-flags.json + env overrides)
    is_feature_enabled(flag_name) -> bool
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    # utf-8-sig transparently strips a BOM if present.
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _coerce(value: str, type_name: str) -> Any:
    if type_name == "boolean":
        return value.strip().lower() in ("1", "true", "yes", "on")
    if type_name in ("number", "integer"):
        try:
            return float(value) if type_name == "number" else int(value)
        except ValueError:
            raise ValueError(f"Cannot coerce {value!r} to {type_name}")
    return value


def _apply_env_overrides(base: Dict[str, Any], spec: Dict[str, Any]) -> Dict[str, Any]:
    """Apply env var overrides described in feature-flags.json:env_variables."""
    out = dict(base)
    for var, meta in spec.items():
        if meta.get("required") and var not in os.environ:
            # Required-but-missing: keep default (caller can validate separately).
            continue
        if var in os.environ:
            out[var] = _coerce(os.environ[var], meta.get("type", "string"))
        else:
            out.setdefault(var, meta.get("default"))
    return out


@lru_cache(maxsize=None)
def load_feature_flags() -> Dict[str, Any]:
    cfg = _read_json(CONFIG_DIR / "feature-flags.json")
    env_spec = cfg.get("env_variables", {})
    cfg["_env_resolved"] = _apply_env_overrides({}, env_spec)
    # Allow VIETLOTT_LOG_LEVEL / VIETLOTT_DEBUG to override environment block.
    if "VIETLOTT_LOG_LEVEL" in os.environ:
        cfg["environment"]["log_level"] = os.environ["VIETLOTT_LOG_LEVEL"]
    if "VIETLOTT_DEBUG" in os.environ:
        cfg["environment"]["debug"] = _coerce(os.environ["VIETLOTT_DEBUG"], "boolean")
    if "VIETLOTT_INVESTMENT_RETURN_RATE" in os.environ:
        cfg["calculation"]["investment_assumed_return_rate"] = _coerce(
            os.environ["VIETLOTT_INVESTMENT_RETURN_RATE"], "number"
        )
    return cfg


@lru_cache(maxsize=None)
def load_settings() -> Dict[str, Any]:
    return _read_json(CONFIG_DIR / "skill-settings.json")


@lru_cache(maxsize=None)
def load_games() -> Dict[str, Any]:
    return _read_json(CONFIG_DIR / "games.json")


@lru_cache(maxsize=None)
def load_resources() -> Dict[str, Any]:
    return _read_json(CONFIG_DIR / "resources.json")


def is_feature_enabled(flag_name: str) -> bool:
    flags = load_feature_flags().get("feature_flags", {})
    if flag_name not in flags:
        raise KeyError(f"Unknown feature flag: {flag_name}")
    return bool(flags[flag_name])


def validate_required_configs() -> None:
    """Ensure all required config files are present and parse as JSON."""
    required = ["feature-flags.json", "feature-flags.schema.json", "games.json", "resources.json", "skill-settings.json"]
    missing = [f for f in required if not (CONFIG_DIR / f).exists()]
    if missing:
        raise FileNotFoundError(f"Missing config files: {missing}")
    for f in required:
        if f.endswith(".schema.json"):
            continue
        _read_json(CONFIG_DIR / f)  # raises on invalid JSON


def investment_return_rate() -> float:
    return float(load_feature_flags()["calculation"]["investment_assumed_return_rate"])


def main() -> None:
    validate_required_configs()
    ff = load_feature_flags()
    print("Config validation: OK")
    print(f"Skill            : {ff['skill_name']} v{ff['version']}")
    print(f"Environment      : {ff['environment']['name']} (log={ff['environment']['log_level']})")
    print(f"LLM temp/retries : {ff['llm']['default_temperature']} / max_attempts={ff['llm']['retry']['max_attempts']}")
    print(f"Currency         : {ff['calculation']['currency']}")
    enabled = [k for k, v in ff["feature_flags"].items() if v]
    print(f"Enabled flags    : {len(enabled)}")
    print(f"Games configured : {list(load_games()['vietlott_games'].keys())}")
    print(f"Risk keywords    : {len(load_settings()['skill_settings']['risk_detection']['keywords_en'])} EN, "
          f"{len(load_settings()['skill_settings']['risk_detection']['keywords_vi'])} VI")


if __name__ == "__main__":
    main()
