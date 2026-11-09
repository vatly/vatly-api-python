from pathlib import Path

import pytest
import yaml


@pytest.fixture(scope="session")
def spec():
    return yaml.safe_load((Path(__file__).parents[1] / "openapi.yaml").read_text())


def example(schema, spec):
    if "$ref" in schema:
        return example(spec["components"]["schemas"][schema["$ref"].split("/")[-1]], spec)
    if "allOf" in schema:
        result = {}
        for part in schema["allOf"]:
            result.update(example(part, spec))
        return result
    if "oneOf" in schema and "properties" not in schema:
        return example(schema["oneOf"][0], spec)
    if "const" in schema:
        return schema["const"]
    if "enum" in schema:
        return schema["enum"][0]
    kind = schema.get("type", "object")
    if isinstance(kind, list):
        if "null" in kind:
            return None
        kind = kind[0]
    if kind == "object":
        return {
            k: example(v, spec)
            for k, v in schema.get("properties", {}).items()
            if k in schema.get("required", [])
        }
    if kind == "array":
        return [example(schema["items"], spec)]
    if "example" in schema:
        return schema["example"]
    if kind == "boolean":
        return True
    if kind in ("integer", "number"):
        return schema.get("minimum", 1)
    if kind == "null":
        return None
    return {"date-time": "2026-01-01T00:00:00Z", "date": "2026-01-01"}.get(
        schema.get("format"), "example"
    )
