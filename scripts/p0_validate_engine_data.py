"""Tasks 0.29/0.30 (reused at 3.31): validate an engine_data JSON file against the contract.

Standard library only. Supports the JSON Schema keywords used in engine_data.schema.json,
plus cross-field checks the schema cannot express (matching array lengths, known keys, size).

Usage: python3 scripts/p0_validate_engine_data.py [path/to/engine_data.json]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "contract" / "engine_data.schema.json").read_text(encoding="utf-8"))
MAX_BYTES = 1_000_000  # NFR-04
TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def resolve(node):
    while "$ref" in node:
        ref = node["$ref"]
        target = SCHEMA
        for part in ref.lstrip("#/").split("/"):
            target = target[part]
        node = {**target, **{k: v for k, v in node.items() if k != "$ref"}}
    return node


def type_ok(value, t):
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, TYPES[t])


def check(value, node, path, errors):
    node = resolve(node)
    if "type" in node:
        types = node["type"] if isinstance(node["type"], list) else [node["type"]]
        if not any(type_ok(value, t) for t in types):
            errors.append(f"{path}: expected {types}, got {type(value).__name__}")
            return
    if "enum" in node and value not in node["enum"]:
        errors.append(f"{path}: {value!r} not in {node['enum']}")
    if "const" in node and value != node["const"]:
        errors.append(f"{path}: expected {node['const']!r}")
    if isinstance(value, str) and "pattern" in node and not re.search(node["pattern"], value):
        errors.append(f"{path}: {value!r} does not match {node['pattern']}")
    if type_ok(value, "number"):
        if "minimum" in node and value < node["minimum"]:
            errors.append(f"{path}: {value} < {node['minimum']}")
        if "maximum" in node and value > node["maximum"]:
            errors.append(f"{path}: {value} > {node['maximum']}")
    if isinstance(value, list):
        if len(value) < node.get("minItems", 0):
            errors.append(f"{path}: fewer than {node['minItems']} items")
        if "maxItems" in node and len(value) > node["maxItems"]:
            errors.append(f"{path}: more than {node['maxItems']} items")
        if "items" in node:
            for i, item in enumerate(value):
                check(item, node["items"], f"{path}[{i}]", errors)
    if isinstance(value, dict):
        for key in node.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing {key!r}")
        props = node.get("properties", {})
        for key, item in value.items():
            if "propertyNames" in node:
                check(key, node["propertyNames"], f"{path}<key {key!r}>", errors)
            if key in props:
                check(item, props[key], f"{path}.{key}", errors)
            elif node.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected key {key!r}")
            elif isinstance(node.get("additionalProperties"), dict):
                check(item, node["additionalProperties"], f"{path}.{key}", errors)


def cross_checks(data, errors):
    units, crops = set(data["units"]), set(data["crops"])
    for section in ("sufficiency", "yield_draws", "price", "backtest"):
        for key in data[section]:
            unit, crop = key.split("|")
            if unit not in units or crop not in crops:
                errors.append(f"{section}.{key}: unknown unit or crop")
    for unit, w in data["weather"].items():
        if unit not in units:
            errors.append(f"weather.{unit}: unknown unit")
        if len(w["seasons"]) != len(w["jas_rain_mm"]):
            errors.append(f"weather.{unit}: seasons and jas_rain_mm lengths differ")
    for key, y in data["yield_draws"].items():
        if len(y["weather_seasons"]) != len(y["q_per_acre"]):
            errors.append(f"yield_draws.{key}: weather_seasons and q_per_acre lengths differ")
        if not y["rel_errors"]:
            errors.append(f"yield_draws.{key}: rel_errors is empty")
    for key, p in data["price"].items():
        if len(p["log_errors"]) != len(p["error_seasons"]):
            errors.append(f"price.{key}: log_errors and error_seasons lengths differ")
    for crop in crops:
        for section in ("costs", "msp"):
            if crop not in data[section]:
                errors.append(f"{section}: missing crop {crop!r}")


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "contract" / "engine_data.mock.json"
    raw = path.read_bytes()
    data = json.loads(raw)
    errors = []
    check(data, SCHEMA, "$", errors)
    if not errors:
        cross_checks(data, errors)
    if len(raw) > MAX_BYTES:
        errors.append(f"file is {len(raw)} bytes, over the {MAX_BYTES} limit (NFR-04)")
    if errors:
        print(f"FAIL {path.name}: {len(errors)} error(s)")
        for e in errors[:50]:
            print("  " + e)
        sys.exit(1)
    print(f"PASS {path.name} ({len(raw) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
