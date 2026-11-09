import asyncio
import inspect
import json
import re
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path

import httpx
import pytest
from conftest import example

import vatly
from vatly import AsyncVatlyClient, RequestOptions, VatlyClient
from vatly.models import CreateCheckoutRequest, UpdateCustomerRequest
from vatly.webhooks import (
    compute_signature_v1,
    construct_webhook_event,
    verify_webhook_signature,
)

KEY = "test_" + "x" * 20
LINK = {"href": "https://api.vatly.com/v1/customers", "type": "application/json"}
CUSTOMER = {
    "id": "customer_a",
    "resource": "customer",
    "testmode": True,
    "email": "test@example.com",
    "name": None,
    "createdAt": "2026-01-01T00:00:00Z",
    "metadata": [],
    "links": {"self": LINK},
}


def operation_cases():
    import yaml

    spec = yaml.safe_load((Path(__file__).parents[1] / "openapi.yaml").read_text())
    inventory = (Path(__file__).parents[1] / "docs/API.md").read_text()
    namespace = None
    cases = []
    for line in inventory.splitlines():
        if line.startswith("## `"):
            namespace = line.split("`")[1]
        match = re.match(r"\| `(\w+)\(.*\)` \| `(\w+) ([^`]+)`", line)
        if match:
            name, method, path = match.groups()
            cases.append((namespace, name, method, path, spec["paths"][path][method.lower()]))
    return cases


def test_inventory_covers_spec(spec):
    expected = {
        (verb.upper(), path)
        for path, item in spec["paths"].items()
        for verb in item
        if verb in {"get", "post", "patch", "put", "delete"}
    }
    assert {(method, path) for _, _, method, path, _ in operation_cases()} == expected


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("namespace,name,method,path,operation", operation_cases())
def test_all_production_operations(spec, asynchronous, namespace, name, method, path, operation):
    response = next(v for code, v in operation["responses"].items() if str(code).startswith("2"))
    schema = response.get("content", {}).get("application/json", {}).get("schema")
    body = example(schema, spec) if schema else None
    calls = []

    def handler(request):
        calls.append(request)
        assert request.method == method
        expected_path = path
        for variable in re.findall(r"{(\w+)}", path):
            expected = variable + "/unsafe?"
            path_value = expected.replace("/", "%2F").replace("?", "%3F")
            expected_path = expected_path.replace("{" + variable + "}", path_value)
        assert request.url.raw_path.decode() == "/v1" + expected_path
        if "requestBody" in operation:
            assert json.loads(request.content) == {"metadata": {"intent": "unit-test"}}
        assert request.headers["Authorization"] == f"Bearer {KEY}"
        return httpx.Response(200, json=body) if schema else httpx.Response(204)

    async def run_async():
        async with AsyncVatlyClient(KEY, transport=httpx.MockTransport(handler)) as client:
            fn = getattr(getattr(client, namespace), name)
            result = await fn(**arguments(fn))
            assert (result is None) == (schema is None)

    def arguments(fn):
        args = {}
        ids = re.findall(r"{(\w+)}", path)
        for key in inspect.signature(fn).parameters:
            if key.endswith("_id"):
                args[key] = (
                    next(v for v in ids if v.lower() == key.replace("_", "").lower()) + "/unsafe?"
                )
            elif key == "body":
                args[key] = {"metadata": {"intent": "unit-test"}}
        return args

    if asynchronous:
        asyncio.run(run_async())
    else:
        with VatlyClient(KEY, transport=httpx.MockTransport(handler)) as client:
            fn = getattr(getattr(client, namespace), name)
            result = fn(**arguments(fn))
            assert (result is None) == (schema is None)
    assert len(calls) == 1


def test_models_aliases_explicit_null_and_timeouts():
    seen = []

    def handler(r):
        seen.append(r)
        return httpx.Response(200, json=CUSTOMER)

    with VatlyClient(KEY, transport=httpx.MockTransport(handler)) as client:
        result = client.customers.update(
            "customer_a", UpdateCustomerRequest(name=None), options=RequestOptions(timeout=0)
        )
        assert result.metadata.root == {}
        assert json.loads(seen[0].content) == {"name": None}
        assert seen[0].extensions["timeout"]["read"] is None
    request = CreateCheckoutRequest(
        redirect_url_success="https://a.test/ok",
        redirect_url_canceled="https://a.test/no",
        products=[{"id": "one_off_product_a", "quantity": 2}],
    )
    assert (
        request.model_dump(by_alias=True, exclude_unset=True)["redirectUrlSuccess"]
        == "https://a.test/ok"
    )


@pytest.mark.parametrize(
    "status,error",
    [
        (401, vatly.VatlyAuthError),
        (403, vatly.VatlyForbiddenError),
        (404, vatly.VatlyNotFoundError),
        (409, vatly.VatlyConflictError),
        (422, vatly.VatlyValidationError),
        (429, vatly.VatlyRateLimitError),
        (503, vatly.VatlyApiError),
    ],
)
def test_errors(status, error):
    with VatlyClient(
        KEY,
        max_retries=0,
        transport=httpx.MockTransport(
            lambda r: httpx.Response(
                status,
                json={
                    "message": "denied",
                    "errors": {"email": ["bad"]},
                    "details": {"reason": "test"},
                },
                headers={"Retry-After": "4"},
            )
        ),
    ) as c:
        with pytest.raises(error) as caught:
            c.customers.list()
    assert caught.value.status == status
    assert caught.value.errors == {"email": ["bad"]}
    assert caught.value.retry_after == 4
    assert caught.value.details == {"reason": "test"}


@pytest.mark.parametrize(
    "status,outcome,keyed,attempts",
    [
        (503, None, True, 3),
        (429, None, True, 3),
        (409, "in_progress", True, 3),
        (409, "unknown", True, 1),
        (409, "conflict", True, 1),
        (503, None, False, 1),
        (422, None, True, 1),
    ],
)
@pytest.mark.parametrize("asynchronous", [False, True])
def test_retry_safety(monkeypatch, status, outcome, keyed, attempts, asynchronous):
    monkeypatch.setattr("vatly._transport.time.sleep", lambda t: None)

    async def no_sleep(t):
        pass

    monkeypatch.setattr("vatly._transport.asyncio.sleep", no_sleep)
    seen = []

    def handler(r):
        seen.append(r)
        return httpx.Response(
            status, json={"details": {"idempotency_outcome": outcome}}, headers={"Retry-After": "0"}
        )

    kwargs = {
        "transport": httpx.MockTransport(handler),
        "idempotency_key_generator": (lambda: "fixed-key") if keyed else None,
    }

    async def run():
        async with AsyncVatlyClient(KEY, **kwargs) as c:
            with pytest.raises(vatly.VatlyError):
                await c.customers.create({"email": "a@b.test"})

    if asynchronous:
        asyncio.run(run())
    else:
        with VatlyClient(KEY, **kwargs) as c:
            with pytest.raises(vatly.VatlyError):
                c.customers.create({"email": "a@b.test"})
    assert len(seen) == attempts
    assert {r.headers.get("Idempotency-Key") for r in seen} == ({"fixed-key"} if keyed else {None})


@pytest.mark.parametrize(
    "failure,error",
    [
        (httpx.ReadTimeout, vatly.VatlyTimeoutError),
        (httpx.ConnectError, vatly.VatlyConnectionError),
    ],
)
def test_network_errors_retry_and_retain_cause(monkeypatch, failure, error):
    monkeypatch.setattr("vatly._transport.time.sleep", lambda t: None)
    seen = []

    def handler(r):
        seen.append(r)
        raise failure("offline", request=r)

    with VatlyClient(KEY, transport=httpx.MockTransport(handler)) as c:
        with pytest.raises(error) as caught:
            c.customers.list()
    assert len(seen) == 3
    assert isinstance(caught.value.__cause__, failure)


def test_retry_after_date_and_header_precedence(monkeypatch):
    delays = []
    seen = []
    monkeypatch.setattr("vatly._transport.time.sleep", delays.append)

    def handler(r):
        seen.append(r)
        if len(seen) == 1:
            return httpx.Response(
                429,
                headers={
                    "Retry-After": format_datetime(
                        datetime.now(timezone.utc) + timedelta(seconds=20)
                    )
                },
            )
        return httpx.Response(200, json=CUSTOMER)

    with VatlyClient(
        KEY,
        transport=httpx.MockTransport(handler),
        default_headers={"idempotency-key": "default"},
        client_info={"app": "Test;\r\nInjected/1"},
    ) as c:
        c.customers.create(
            {"email": "a@b.test"},
            options=RequestOptions(
                idempotency_key="override", headers={"IDEMPOTENCY-KEY": "header"}, timeout=3
            ),
        )
    assert 18 <= delays[0] <= 20
    assert all(r.headers["Idempotency-Key"] == "override" for r in seen)
    assert seen[0].extensions["timeout"]["read"] == 3
    assert "Injected/1" in seen[0].headers["Vatly-Client-Info"]


@pytest.mark.parametrize("asynchronous", [False, True])
def test_cursor_pagination_uses_same_endpoint_and_rejects_loops(asynchronous):
    seen = []

    def handler(r):
        seen.append(r)
        assert r.url.host == "api.vatly.com"
        assert r.url.path == "/v1/customers"
        return httpx.Response(
            200,
            json={
                "data": [CUSTOMER],
                "count": 1,
                "links": {
                    "self": LINK,
                    "prev": None,
                    "next": {**LINK, "href": "https://evil.test/?startingAfter=customer_next"},
                },
            },
        )

    async def run():
        async with AsyncVatlyClient(KEY, transport=httpx.MockTransport(handler)) as c:
            with pytest.raises(vatly.VatlyPaginationError):
                async for customer in c.customers.list_all(
                    {"endingBefore": "initial", "email": "test@example.com"}
                ):
                    assert customer.id == "customer_a"

    if asynchronous:
        asyncio.run(run())
    else:
        with VatlyClient(KEY, transport=httpx.MockTransport(handler)) as c:
            with pytest.raises(vatly.VatlyPaginationError):
                list(c.customers.list_all({"endingBefore": "initial", "email": "test@example.com"}))
    assert len(seen) == 2
    assert seen[1].url.params["startingAfter"] == "customer_next"
    assert "endingBefore" not in seen[1].url.params
    assert seen[1].url.params["email"] == "test@example.com"


def test_configuration_and_test_helper_guard():
    for kwargs in [
        {"timeout": -1},
        {"timeout": float("nan")},
        {"max_retries": -1},
        {"max_retries": 1.5},
    ]:
        with pytest.raises(ValueError):
            VatlyClient(KEY, **kwargs)
    with pytest.raises(ValueError):
        VatlyClient("bad")
    with VatlyClient("live_" + "x" * 20) as c:
        with pytest.raises(ValueError):
            c.test_helpers.simulate_order_payment("order_a", {"paymentStatus": "paid"})


def test_invalid_success_and_boolean_query():
    seen = []

    def handler(r):
        seen.append(r)
        return httpx.Response(204) if r.method == "DELETE" else httpx.Response(200, text="not-json")

    with VatlyClient(KEY, transport=httpx.MockTransport(handler)) as c:
        c.subscriptions.cancel("subscription_a", {"immediately": True})
        assert seen[0].url.params["immediately"] == "1"
        with pytest.raises(vatly.VatlyApiError):
            c.customers.get("a")
    assert len(seen) == 2  # Invalid 2xx is not a transient error.


def test_locked_webhook_vector_and_boundaries():
    raw = b'{"foo":"bar"}'
    expected = "f5a64398fd049d1507a2654439f257e7549fcff6ffa9bbc355c7f1ebaefb6925"
    assert compute_signature_v1(raw, "my_secret_key", 1700000000) == expected
    header = f"v2=ignored,t=1700000000,v1={expected.upper()}"
    verify_webhook_signature(raw, header, ["old", "my_secret_key"], now=1700000300)
    for bad_raw, bad_header, now in [
        (raw + b" ", header, 1700000000),
        (raw, header, 1700000301),
        (raw, header, 1699999699),
        (raw, "v1=" + expected, 1700000000),
    ]:
        with pytest.raises(vatly.VatlyInvalidSignatureError):
            verify_webhook_signature(bad_raw, bad_header, "my_secret_key", now=now)


def test_webhook_setup_and_unknown_events(spec):
    setup = example(spec["components"]["schemas"]["Webhook"], spec)
    for event_name, obj, known in [
        ("webhook.setup", setup, True),
        ("future.created", {"arbitrary": 1}, False),
    ]:
        payload = {
            "id": "webhook_event_a",
            "resource": "webhook_event",
            "eventName": event_name,
            "reason": None,
            "entityType": "webhook",
            "entityId": "webhook_a",
            "object": obj,
            "createdAt": "2026-01-01T00:00:00Z",
            "testmode": True,
            "known": not known,
        }
        raw = json.dumps(payload).encode()
        header = "t=1700000000,v1=" + compute_signature_v1(raw, "secret", 1700000000)
        event = construct_webhook_event(raw, header, "secret", now=1700000000)
        assert event.known is known
        assert event.id == "webhook_event_a"
        assert event.event_name == event_name
        if known:
            assert event.object.resource == "webhook"
        else:
            assert event.object == {"arbitrary": 1}
