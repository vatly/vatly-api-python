"""Execute the documentation's Python fences through the real SDK transport."""

import asyncio
import hashlib
import hmac
import inspect
import json
import re
import time
from pathlib import Path

import httpx
import pytest
from conftest import example

from vatly import VatlyClient

DOCS = Path(__file__).parents[1] / "docs"
CASES = [
    pytest.param(page, index, code, id=f"{page.stem}-{index}")
    for page in sorted(DOCS.glob("*.md"))
    for index, code in enumerate(re.findall(r"```python\n(.*?)```", page.read_text(), re.S))
]


@pytest.mark.parametrize("page,index,code", CASES)
def test_documented_examples(page, index, code, spec, monkeypatch):
    calls = []

    def respond(request):
        calls.append(request)
        assert request.url.host == "api.vatly.com"
        if request.url.path.endswith("/customer_missing"):
            return httpx.Response(404, json={"message": "not found"})
        for path, operations in spec["paths"].items():
            if not re.fullmatch("/v1" + re.sub(r"\{[^}]+\}", "[^/]+", path), request.url.path):
                continue
            operation = operations[request.method.lower()]
            response = next(v for k, v in operation["responses"].items() if str(k).startswith("2"))
            schema = response.get("content", {}).get("application/json", {}).get("schema")
            if schema is None:
                return httpx.Response(204)
            value = example(schema, spec)
            if isinstance(value, dict) and "data" in value:
                value["links"]["next"] = None
            return httpx.Response(200, json=value)
        raise AssertionError(f"Undocumented endpoint: {request.method} {request.url}")

    for cls in (httpx.Client, httpx.AsyncClient):
        original = cls.__init__

        def initialize(self, *args, _original=original, **kwargs):
            kwargs["transport"] = kwargs.get("transport") or httpx.MockTransport(respond)
            _original(self, *args, **kwargs)

        monkeypatch.setattr(cls, "__init__", initialize)
    monkeypatch.setenv("VATLY_API_KEY", "test_" + "x" * 20)
    stamp = int(time.time())
    raw = json.dumps(
        {
            "id": "event_docs",
            "resource": "webhook_event",
            "eventName": "future.event",
            "reason": None,
            "entityType": "future",
            "entityId": "future_1",
            "object": {},
            "testmode": True,
            "createdAt": "2026-01-01T00:00:00Z",
        }
    ).encode()
    digest = hmac.new(b"secret", str(stamp).encode() + b"." + raw, hashlib.sha256).hexdigest()
    namespace = {"__name__": "docs_example"}
    exec(compile(code, f"{page}:{index}", "exec"), namespace)
    function = namespace["example"]
    with VatlyClient() as client:
        available = {
            "client": client,
            "raw_body": raw,
            "signature": f"t={stamp},v1={digest}",
            "secret": "secret",
        }
        result = function(
            **{name: available[name] for name in inspect.signature(function).parameters}
        )
        if inspect.isawaitable(result):
            result = asyncio.run(result)
    if page.stem == "Webhooks":
        assert result is True or result == ("event_docs", "future.event", False)
    else:
        assert calls


def test_overview_links_every_flat_page():
    overview = (DOCS / "README.md").read_text()
    assert not any(path.is_dir() for path in DOCS.iterdir())
    for page in DOCS.glob("*.md"):
        if page.name != "README.md":
            assert f"]({page.name})" in overview
