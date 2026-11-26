import asyncio
import inspect
import json
import platform
import re
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path

import httpx
import pytest
from conftest import example
from pydantic import ValidationError

import vatly
from vatly import AsyncVatlyClient, RequestOptions, VatlyClient
from vatly.models import CreateCheckoutRequest, Money, UpdateCustomerRequest
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


def example_schema(schema, spec):
    if "$ref" in schema:
        return spec["components"]["schemas"][schema["$ref"].split("/")[-1]]
    return schema


def test_inventory_covers_spec(spec):
    expected = {
        (verb.upper(), path)
        for path, item in spec["paths"].items()
        for verb in item
        if verb in {"get", "post", "patch", "put", "delete"}
    }
    assert {(method, path) for _, _, method, path, _ in operation_cases()} == expected


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "namespace,name,method,path,operation",
    [case for case in operation_cases() if case[1].startswith("list")],
)
def test_all_paginated_resources(spec, asynchronous, namespace, name, method, path, operation):
    schema = operation["responses"]["200"]["content"]["application/json"]["schema"]
    page = example(schema, spec)
    first = page["data"][0]
    second = {**first, "id": first["id"] + "second"}
    calls = []

    def respond(request):
        calls.append(request)
        assert request.url.params["limit"] == "1"
        assert request.headers["X-Trace"] == "pagination"
        if len(calls) == 1:
            assert request.url.params["endingBefore"] == "initial"
            return httpx.Response(
                200,
                json={
                    **page,
                    "data": [first],
                    "count": 1,
                    "links": {
                        **page["links"],
                        "next": {
                            "href": "https://untrusted.test/?startingAfter=next_cursor",
                            "type": "application/json",
                        },
                    },
                },
            )
        assert request.url.host == "api.vatly.com"
        assert request.url.params["startingAfter"] == "next_cursor"
        assert "endingBefore" not in request.url.params
        return httpx.Response(
            200,
            json={
                **page,
                "data": [second],
                "count": 1,
                "links": {**page["links"], "next": None},
            },
        )

    def iterator(client):
        iterator_name = name.replace("list", "list_all", 1)
        fn = getattr(getattr(client, namespace), iterator_name)
        args = {key: "parent_id" for key in inspect.signature(fn).parameters if key.endswith("_id")}
        return fn(
            **args,
            params={"limit": 1, "endingBefore": "initial"},
            options=RequestOptions(headers={"X-Trace": "pagination"}),
        )

    async def run():
        async with AsyncVatlyClient(KEY, transport=httpx.MockTransport(respond)) as client:
            return [item.id async for item in iterator(client)]

    if asynchronous:
        ids = asyncio.run(run())
    else:
        with VatlyClient(KEY, transport=httpx.MockTransport(respond)) as client:
            ids = [item.id for item in iterator(client)]
    assert ids == [first["id"], second["id"]]
    assert len(calls) == 2


@pytest.mark.parametrize("raw", [b"not json", b"[]", b"{}", b"null"])
def test_signed_invalid_envelopes_are_rejected(raw):
    from vatly.webhooks import construct_event

    signature = "t=100,v1=" + compute_signature_v1(raw, "secret", 100)
    for construct in (construct_event, construct_webhook_event):
        with pytest.raises(vatly.VatlyInvalidSignatureError, match="envelope"):
            construct(raw, signature, "secret", now=100)


@pytest.mark.parametrize("header", [None, "", "t=-1,v1=bad", "t=100,v1=bad"])
def test_boolean_signature_verification_rejects_missing_or_malformed_headers(header):
    from vatly.webhooks import is_valid_webhook_signature

    assert not is_valid_webhook_signature(b"{}", header, "secret", now=100)
    signature = "t=100,v1=" + compute_signature_v1(b"{}", "secret", 100)
    assert is_valid_webhook_signature(b"{}", signature, "secret", now=100)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("namespace,name,method,path,operation", operation_cases())
def test_all_production_operations(spec, asynchronous, namespace, name, method, path, operation):
    response = next(v for code, v in operation["responses"].items() if str(code).startswith("2"))
    schema = response.get("content", {}).get("application/json", {}).get("schema")
    body = example(schema, spec) if schema else None
    request_body = None
    if "requestBody" in operation:
        request_schema = operation["requestBody"]["content"]["application/json"]["schema"]
        request_body = example(request_schema, spec)
        if "metadata" in example_schema(request_schema, spec).get("properties", {}):
            request_body["metadata"] = {"intent": "unit-test"}
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
            assert json.loads(request.content) == request_body
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
                args[key] = request_body
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


def test_order_line_related_subscription_is_typed_and_nullable(spec):
    order = example(spec["components"]["schemas"]["Order"], spec)
    line = order["lines"][0]
    order["lines"] = [
        {
            **line,
            "productType": "subscription_plan",
            "productId": "subscription_plan_a",
            "relatedResources": {"subscriptionId": "subscription_a"},
        },
        {**line, "productType": "subscription_plan", "relatedResources": {"subscriptionId": None}},
        {**line, "productType": "one_off_product", "relatedResources": None},
        line,  # Older payloads omit relatedResources.
    ]
    with VatlyClient(
        KEY, transport=httpx.MockTransport(lambda r: httpx.Response(200, json=order))
    ) as c:
        signup, unresolved, unrelated, older = c.orders.get("order_a").lines
    assert "relatedResources" not in line
    assert signup.related_resources.subscription_id == "subscription_a"
    assert signup.product_id == "subscription_plan_a"
    assert unresolved.related_resources is not None
    assert unresolved.related_resources.subscription_id is None
    assert unrelated.related_resources is None
    assert older.related_resources is None
    wire = [ln.model_dump(by_alias=True, exclude_unset=True) for ln in (signup, unresolved)]
    assert wire[0]["relatedResources"] == {"subscriptionId": "subscription_a"}
    assert wire[1]["relatedResources"] == {"subscriptionId": None}


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
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("attached_request", [False, True])
def test_network_errors_retry_and_retain_cause(
    monkeypatch, failure, error, asynchronous, attached_request
):
    monkeypatch.setattr("vatly._transport.time.sleep", lambda t: None)

    async def no_sleep(t):
        pass

    monkeypatch.setattr("vatly._transport.asyncio.sleep", no_sleep)
    seen = []

    def handler(r):
        seen.append(r)
        raise failure("offline", request=r if attached_request else None)

    async def run():
        async with AsyncVatlyClient(KEY, transport=httpx.MockTransport(handler)) as c:
            await c.customers.list({"limit": 7})

    with pytest.raises(error) as caught:
        if asynchronous:
            asyncio.run(run())
        else:
            with VatlyClient(KEY, transport=httpx.MockTransport(handler)) as c:
                c.customers.list({"limit": 7})
    assert len(seen) == 3
    assert isinstance(caught.value.__cause__, failure)
    assert caught.value.method == "GET"
    assert caught.value.url == "https://api.vatly.com/v1/customers?limit=7"


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("status,body", [(200, b""), (204, b""), (200, b"not-json")])
def test_typed_resource_rejects_invalid_success(asynchronous, status, body):
    def handler(r):
        return httpx.Response(status, content=body)

    async def run():
        async with AsyncVatlyClient(KEY, transport=httpx.MockTransport(handler)) as c:
            await c.customers.get("customer_a")

    with pytest.raises(vatly.VatlyApiError, match="Invalid Vatly response") as caught:
        if asynchronous:
            asyncio.run(run())
        else:
            with VatlyClient(KEY, transport=httpx.MockTransport(handler)) as c:
                c.customers.get("customer_a")
    assert caught.value.status == status
    assert caught.value.method == "GET"
    assert caught.value.url == "https://api.vatly.com/v1/customers/customer_a"


@pytest.mark.parametrize("currency", ["EUR", "USD"])
def test_money_preserves_enabled_currency_precision_contract(currency):
    assert Money.model_validate({"value": "10.00", "currency": currency}).root.value == "10.00"
    for value in ["10", "10.0", "10.000"]:
        with pytest.raises(ValidationError):
            Money.model_validate({"value": value, "currency": currency})
    for value, disabled in [("1000", "JPY"), ("1.000", "BHD")]:
        with pytest.raises(ValidationError):
            Money.model_validate({"value": value, "currency": disabled})


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


def test_user_agent_chains_package_tokens():
    seen = []

    def handler(r):
        seen.append(r)
        return httpx.Response(200, json=CUSTOMER)

    transport = httpx.MockTransport(handler)
    for headers in (None, {"user-agent": "Custom/1"}):
        with VatlyClient(KEY, transport=transport, default_headers=headers) as c:
            c.customers.get("customer_a")
            c.add_version_string("vatly/vatly-fluent-python/1.2.3")
            c.add_version_string(" vatly/vatly-django/4 5 ")
            c.add_version_string("vatly/vatly-fluent-python/1.2.3")
            c.customers.get("customer_a")
            c.customers.get("customer_a", options=RequestOptions(headers={"User-Agent": "Own/1"}))
    sdk = f"vatly/vatly-api-python/{vatly.__version__}"
    runtime = f"Python/{platform.python_version()} httpx/{httpx.__version__}"
    assert [r.headers["User-Agent"] for r in seen] == [
        f"{sdk} {runtime}",
        f"{sdk} {runtime} vatly/vatly-fluent-python/1.2.3 vatly/vatly-django/4-5",
        "Own/1",
        "Custom/1",
        "Custom/1",
        "Own/1",
    ]


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


def _sent_bodies(*calls):
    seen = []

    def handler(r):
        seen.append(json.loads(r.content))
        return httpx.Response(204)

    with VatlyClient(KEY, transport=httpx.MockTransport(handler)) as client:
        for call in calls:
            # The stub's empty 204 is not a resource; only the sent body matters here.
            with pytest.raises(vatly.VatlyApiError, match="Invalid Vatly response"):
                call(client)
    return seen


def test_request_bodies_send_spec_fields_and_spec_nulls_only():
    from vatly.models import UpdateSubscriptionRequest

    product = {"id": "subscription_plan_a", "price": None, "trialDays": None, "metadata": None}
    sent = _sent_bodies(
        # Dictionary input: unknown and non-nullable null fields are dropped at every level.
        lambda c: c.checkouts.create(
            {
                "redirectUrlSuccess": "https://a.test/ok",
                "redirectUrlCanceled": "https://a.test/no",
                "products": [{**product, "quantity": None, "unknown": 1}],
                "metadata": None,
                "unknownTopLevel": "x",
            }
        ),
        lambda c: c.customers.create({"email": "a@b.test", "metadata": None}),
        lambda c: c.orders.create_full_refund("order_a", {"metadata": None}),
        lambda c: c.orders.create_refund(
            "order_a",
            {
                "items": [{"itemId": "a", "amount": {"value": "1.00", "currency": "EUR"}}],
                "metadata": None,
            },
        ),
        # Model input, including extra attributes the model allows.
        lambda c: c.subscriptions.update(
            "subscription_a",
            UpdateSubscriptionRequest(quantity=None, anchor=None, prorate=True, extra=1),
        ),
        lambda c: c.subscriptions.update(
            "subscription_a", {"anchor": "2026-02-01", "trialUntil": "2026-02-01T10:00:00Z"}
        ),
    )
    assert sent[0] == {
        "redirectUrlSuccess": "https://a.test/ok",
        "redirectUrlCanceled": "https://a.test/no",
        "products": [product],
        "metadata": None,
    }
    assert sent[1] == {"email": "a@b.test", "metadata": None}
    assert sent[2] == {"metadata": None}
    assert sent[3]["metadata"] is None
    assert sent[4] == {"prorate": True, "anchor": None}
    assert sent[5] == {"anchor": "2026-02-01", "trialUntil": "2026-02-01T10:00:00Z"}


@pytest.mark.parametrize(
    "body",
    [
        {"trialDays": 0},
        {"trialDays": -1},
        {"metadata": {"k": 1}},
        {"metadata": {"k" * 41: "v"}},
        {"metadata": {"k": "v" * 501}},
        {"metadata": {f"k{i}": "v" for i in range(51)}},
        {"metadata": ["v"]},
    ],
)
def test_invalid_checkout_product_input_is_rejected_before_sending(body):
    from vatly.models import CheckoutProduct

    with pytest.raises(ValidationError):
        CheckoutProduct(id="subscription_plan_a", **body)
    with VatlyClient(KEY, transport=httpx.MockTransport(lambda r: pytest.fail())) as c:
        with pytest.raises(ValidationError):
            c.checkouts.create(
                {
                    "redirectUrlSuccess": "https://a.test/ok",
                    "redirectUrlCanceled": "https://a.test/no",
                    "products": [{"id": "subscription_plan_a", **body}],
                }
            )


def test_request_metadata_limits_are_inclusive():
    metadata = {f"{i:040d}": "v" * 500 for i in range(50)}
    sent = _sent_bodies(
        lambda c: c.customers.create({"email": "a@b.test", "metadata": metadata}),
        lambda c: c.orders.create_full_refund("order_a", {"metadata": metadata}),
    )
    assert [body["metadata"] for body in sent] == [metadata, metadata]
    with pytest.raises(ValidationError):
        with VatlyClient(KEY, transport=httpx.MockTransport(lambda r: pytest.fail())) as c:
            c.orders.create_full_refund("order_a", {"metadata": {"a": None}})


def test_refund_metadata_is_typed_in_resources_and_webhooks(spec):
    from vatly.models import Refund

    refund = example(spec["components"]["schemas"]["Refund"], spec)
    assert "metadata" in refund
    assert Refund.model_validate({**refund, "metadata": None}).metadata is None
    parsed = Refund.model_validate({**refund, "metadata": {"ticketId": "SUPPORT-1"}})
    assert parsed.metadata.root == {"ticketId": "SUPPORT-1"}
    payload = example(spec["components"]["schemas"]["WebhookDelivery"], spec)
    payload.update(
        eventName="refund.completed",
        entityType="refund",
        entityId=refund["id"],
        object={**refund, "metadata": {"ticketId": "SUPPORT-1"}},
    )
    raw = json.dumps(payload).encode()
    signature = compute_signature_v1(raw, "secret", 100)
    event = construct_webhook_event(raw, f"t=100,v1={signature}", "secret", now=100)
    assert isinstance(event.object, Refund)
    assert event.object.metadata.root == {"ticketId": "SUPPORT-1"}
