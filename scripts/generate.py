"""Generate models/resources/docs from the pinned production spec. No network access."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def snake(value: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower().replace("-", "_")


def generate(out: Path) -> None:
    spec = yaml.safe_load((ROOT / "openapi.yaml").read_text())
    schemas = spec["components"]["schemas"].copy()
    operations = []
    for path, item in spec["paths"].items():
        for verb, op in item.items():
            if verb not in {"get", "post", "patch", "delete", "put"}:
                continue
            name = op["operationId"]
            params = [
                spec["components"]["parameters"][p["$ref"].split("/")[-1]] if "$ref" in p else p
                for p in item.get("parameters", []) + op.get("parameters", [])
            ]
            query = [p for p in params if p["in"] == "query"]
            query_type = name[0].upper() + name[1:] + "Params"
            if query:
                schemas[query_type] = {
                    "type": "object",
                    "properties": {p["name"]: p["schema"] for p in query},
                    "required": [p["name"] for p in query if p.get("required")],
                }
            response = next(v for c, v in op["responses"].items() if str(c).startswith("2"))
            schema = response.get("content", {}).get("application/json", {}).get("schema")
            paginated = bool(schema and "data" in schema.get("properties", {}))
            result = "None"
            if schema:
                if "$ref" in schema:
                    result = schema["$ref"].split("/")[-1]
                elif paginated:
                    result = (
                        "Page[" + schema["properties"]["data"]["items"]["$ref"].split("/")[-1] + "]"
                    )
                else:
                    result = name[0].upper() + name[1:] + "Response"
                    schemas[result] = schema
            body = (
                op.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema")
            )
            operations.append(
                (path, verb, op, params, query_type if query else None, result, body, paginated)
            )

    def wire_strings(value):
        if isinstance(value, dict):
            return {
                k: wire_strings(v)
                for k, v in value.items()
                if not (k == "format" and v in ("uri", "uri-reference", "email"))
            }
        if isinstance(value, list):
            return [wire_strings(v) for v in value]
        return value

    schemas = wire_strings(schemas)
    # Resolve Money's outer/branch intersection before codegen: the generator
    # otherwise unions currency enums and drops the two-decimal branch's `not`.
    money = schemas["Money"]
    variants = []
    for branch in money["oneOf"]:
        constraint = branch["properties"]["currency"]
        currencies = [
            currency
            for currency in money["properties"]["currency"]["enum"]
            if currency in constraint.get("enum", [currency])
            and currency not in constraint.get("not", {}).get("enum", [])
        ]
        if not currencies:
            continue
        variant = deepcopy({k: v for k, v in money.items() if k != "oneOf"})
        variant["properties"]["currency"]["enum"] = currencies
        variant["properties"]["value"].update(branch["properties"]["value"])
        variants.append(variant)
    schemas["Money"] = {"description": money["description"], "oneOf": variants}
    # Production currently returns catalogue values such as `digital_download`
    # beyond this output enum. Preserve them; keep request enums constrained.
    schemas["OneOffProduct"]["properties"]["productType"].pop("enum", None)
    schema_file = out / "schema.json"
    schema_file.write_text(
        json.dumps({"$defs": schemas}).replace("#/components/schemas/", "#/$defs/")
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "datamodel_code_generator",
            "--input",
            str(schema_file),
            "--input-file-type",
            "jsonschema",
            "--output",
            str(out / "models.py"),
            "--output-model-type",
            "pydantic_v2.BaseModel",
            "--base-class",
            "vatly._model.VatlyModel",
            "--target-python-version",
            "3.10",
            "--snake-case-field",
            "--allow-population-by-field-name",
            "--use-standard-collections",
            "--use-union-operator",
            "--use-schema-description",
            "--disable-timestamp",
            "--extra-fields",
            "allow",
            "--use-generic-container-types",
            "--use-annotated",
            "--enum-field-as-literal",
            "all",
        ],
        check=True,
    )
    groups = {}
    for operation in operations:
        group = operation[0].split("/")[1]
        groups.setdefault(group, []).append(operation)
    resource_lines = [
        '"""Generated resource interfaces. Run uv run python scripts/generate.py."""',
        "from __future__ import annotations",
        "from collections.abc import Iterator, AsyncIterator",
        "from typing import Any",
        "from urllib.parse import quote",
        "from . import models",
        "from ._transport import SyncTransport, AsyncTransport, RequestOptions",
        "from .pagination import Page, next_params",
    ]
    docs = [
        "# API reference",
        "",
        "Generated from `openapi.yaml`. Sync and async clients expose the same methods.",
        "Pass a Pydantic request/params model or a wire-format dictionary. All methods accept keyword-only `options=RequestOptions(...)`.",
        "",
    ]
    for group, ops in groups.items():
        cls = "".join(part.title() for part in group.split("-"))
        docs.extend(
            [
                f"## `{snake(cls)}`",
                "",
                "| Method | HTTP endpoint | Returns |",
                "| --- | --- | --- |",
            ]
        )
        for asynchronous in (False, True):
            prefix = "Async" if asynchronous else ""
            resource_lines.extend(
                [
                    f"class {prefix}{cls}:",
                    f"    def __init__(self, transport: {prefix or 'Sync'}Transport) -> None:",
                    "        self._transport = transport",
                ]
            )
            for path, verb, op, params, query_type, result, body, paginated in ops:
                name = op["operationId"]
                # Match the JS SDK's resource-relative names, not OpenAPI's global operation ids.
                entity = {
                    "one-off-products": "OneOffProduct",
                    "subscription-plans": "SubscriptionPlan",
                    "webhook-endpoints": "WebhookEndpoint",
                    "webhook-events": "WebhookEvent",
                    "test-helpers": "",
                }.get(group, cls.rstrip("s"))
                method = snake(name.replace(entity, "", 1)) if entity else snake(name)
                method = {
                    "lists": "list",
                    "create_customer_portal_session": "create_portal_session",
                    "fast_forward_subscription_renewal": "fast_forward_renewal",
                    "create_full_order_refund": "create_full_refund",
                }.get(method, method)
                ids = re.findall(r"{(\w+)}", path)
                arguments = ["self"] + [f"{snake(p)}: str" for p in ids]
                if body:
                    arguments.append(f"body: models.{body['$ref'].split('/')[-1]} | dict[str, Any]")
                if query_type:
                    arguments.append(f"params: models.{query_type} | dict[str, Any] | None = None")
                arguments.append("*, options: RequestOptions | None = None")
                typed_result = re.sub(r"\b(?!Page\b|None\b)([A-Z]\w*)", r"models.\1", result)
                signature = f"{method}({', '.join(arguments)})"
                resource_lines.extend(
                    [
                        f"    {'async ' if asynchronous else ''}def {signature} -> {typed_result}:",
                        f'        """{op.get("summary", name)}."""',
                    ]
                )
                if group == "test-helpers":
                    resource_lines.extend(
                        [
                            '        if self._transport.mode != "test":',
                            '            raise ValueError("Test helpers require a test-mode API key")',
                        ]
                    )
                url = re.sub(r"{(\w+)}", lambda m: "{quote(" + snake(m[1]) + ", safe='')}", path)
                result_arg = "type(None)" if result == "None" else typed_result
                resource_lines.append(
                    f"        return {'await ' if asynchronous else ''}self._transport.request({verb.upper()!r}, f{url!r}, {result_arg}, body={'body' if body else 'None'}, params={'params' if query_type else 'None'}, options=options)"
                )
                if not asynchronous:
                    doc_args = (
                        [snake(p) for p in ids]
                        + (["body"] if body else [])
                        + (["params=None"] if query_type else [])
                    )
                    docs.append(
                        f"| `{method}({', '.join(doc_args)})` | `{verb.upper()} {path}` | `{result}` |"
                    )
                if paginated:
                    all_method = method.replace("list", "list_all", 1)
                    item_type = typed_result[len("Page[") : -1]
                    resource_lines.extend(
                        [
                            f"    {'async ' if asynchronous else ''}def {all_method}({', '.join(arguments)}) -> {'AsyncIterator' if asynchronous else 'Iterator'}[{item_type}]:",
                            "        query = self._transport.serialize(params) or {}",
                            "        seen: set[str] = set()",
                            '        if query.get("startingAfter"):',
                            '            seen.add(str(query["startingAfter"]))',
                            "        while True:",
                            f"            page = {'await ' if asynchronous else ''}self.{method}({''.join(snake(p) + ', ' for p in ids)}query, options=options)",
                        ]
                    )
                    if asynchronous:
                        resource_lines.extend(
                            ["            for item in page.data:", "                yield item"]
                        )
                    else:
                        resource_lines.append("            yield from page.data")
                    resource_lines.extend(
                        [
                            "            following = next_params(page, query, seen)",
                            "            if following is None:",
                            "                return",
                            "            query = following",
                        ]
                    )
        docs.append("")
    (out / "resources.py").write_text("\n".join(resource_lines) + "\n")
    (out / "API.md").write_text("\n".join(docs) + "\n")
    lines = [
        '"""Vatly synchronous and asynchronous clients."""',
        "from . import resources",
        "from ._transport import SyncTransport, AsyncTransport",
    ]
    for prefix, base in [("", "SyncTransport"), ("Async", "AsyncTransport")]:
        lines.extend(
            [
                f"class {prefix}VatlyClient({base}):",
                '    """Resources are initialized lazily and share this client\'s connection pool."""',
            ]
        )
        for group in groups:
            cls = "".join(part.title() for part in group.split("-"))
            lines.extend(
                [
                    "    @property",
                    f"    def {snake(cls)}(self) -> resources.{prefix}{cls}:",
                    f"        return resources.{prefix}{cls}(self)",
                ]
            )
    (out / "client.py").write_text("\n".join(lines) + "\n")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--config",
            str(ROOT / "pyproject.toml"),
            "--fix",
            str(out / "models.py"),
            str(out / "resources.py"),
            str(out / "client.py"),
        ],
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            "format",
            "--config",
            str(ROOT / "pyproject.toml"),
            str(out / "models.py"),
            str(out / "resources.py"),
            str(out / "client.py"),
        ],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        generate(out)
        for name in ("models.py", "resources.py", "client.py", "API.md"):
            target = ROOT / ("docs" if name.endswith(".md") else "src/vatly") / name
            if args.check:
                if not target.exists() or target.read_bytes() != (out / name).read_bytes():
                    raise SystemExit(f"Generated file out of date: {target}")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((out / name).read_bytes())


if __name__ == "__main__":
    main()
