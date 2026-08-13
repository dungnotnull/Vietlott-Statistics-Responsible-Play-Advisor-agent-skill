#!/usr/bin/env python3
"""
Self-contained JSON-schema (Draft-07 subset) validator for config files.

Validates config/feature-flags.json against config/feature-flags.schema.json
WITHOUT any third-party dependency (no `jsonschema` package required). Supports
the Draft-07 keywords actually used by our schema: type, required, enum,
const, minimum, maximum, additionalProperties (boolean), properties.

Usage:
    python scripts/validate_config.py
Exit code 0 = valid; 1 = invalid (with a list of violations).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def _type_ok(value: Any, type_name: str) -> bool:
    if type_name == "object":
        return isinstance(value, dict)
    if type_name == "array":
        return isinstance(value, list)
    if type_name == "string":
        return isinstance(value, str)
    if type_name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if type_name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if type_name == "boolean":
        return isinstance(value, bool)
    return False


def _validate(value: Any, schema: Dict[str, Any], path: str, errors: List[str]) -> None:
    if not isinstance(schema, dict):
        return

    if "$ref" in schema or "allOf" in schema or "oneOf" in schema or "anyOf" in schema:
        # Minimal schemas here do not use composition; skip gracefully.
        return

    schema_type = schema.get("type")
    if schema_type is not None:
        if isinstance(schema_type, list):
            if not any(_type_ok(value, t) for t in schema_type):
                errors.append(f"{path}: expected type in {schema_type}, got {type(value).__name__}")
                return
        else:
            if not _type_ok(value, schema_type):
                errors.append(f"{path}: expected type {schema_type}, got {type(value).__name__}")
                return

    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {value!r}")

    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} not in enum {schema['enum']}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} < minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: {value} > maximum {schema['maximum']}")

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key, subschema in props.items():
            if key in value:
                _validate(value[key], subschema, f"{path}.{key}", errors)

        required = schema.get("required", [])
        for req in required:
            if req not in value:
                errors.append(f"{path}: missing required property {req!r}")

        additional = schema.get("additionalProperties")
        if additional is False:
            extra = set(value.keys()) - set(props.keys())
            if extra:
                errors.append(f"{path}: additional properties not allowed: {sorted(extra)}")
        elif isinstance(additional, dict):
            for key, val in value.items():
                if key not in props:
                    _validate(val, additional, f"{path}.{key}", errors)

    if isinstance(value, list) and "items" in schema:
        item_schema = schema["items"]
        for i, item in enumerate(value):
            _validate(item, item_schema, f"{path}[{i}]", errors)


def validate_instance(instance: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    _validate(instance, schema, "$", errors)
    return errors


def main() -> int:
    instance_path = CONFIG_DIR / "feature-flags.json"
    schema_path = CONFIG_DIR / "feature-flags.schema.json"
    if not instance_path.exists():
        print(f"ERROR: missing {instance_path}", file=sys.stderr)
        return 1
    if not schema_path.exists():
        print(f"ERROR: missing {schema_path}", file=sys.stderr)
        return 1

    instance = json.loads(instance_path.read_text(encoding="utf-8-sig"))
    schema = json.loads(schema_path.read_text(encoding="utf-8-sig"))
    errors = validate_instance(instance, schema)

    # Also confirm all JSON configs parse (caught by config_loader too).
    for name in ("games.json", "resources.json", "skill-settings.json"):
        try:
            json.loads((CONFIG_DIR / name).read_text(encoding="utf-8-sig"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"config/{name}: parse error: {exc}")

    if errors:
        print(f"INVALID: {len(errors)} violation(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("Config schema validation: OK")
    print(f"  feature-flags.json validated against feature-flags.schema.json ({len(errors)} violations)")
    print("  games.json, resources.json, skill-settings.json parse OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
