# Vatly Python SDK

> **Alpha — under active development. Every alpha release may include breaking changes. Pin exact versions during alpha.**

Python SDK for Vatly, the merchant of record for AI, software and digital products.
Python 3.10+, Pydantic v2 models, and pooled httpx sync/async clients. All 50 production
OpenAPI operations are covered. No package has been published yet.

## Installation

Once published:

```bash
pip install vatly-sdk==0.1.0a2
```

For local development: `uv sync --locked`.

## Quick start

Get a test or live API key from [the dashboard](https://my.vatly.com), under Settings > API.
Keep keys server-side. The client reads `VATLY_API_KEY` by default.

```python
from vatly import VatlyClient
from vatly.models import CreateCheckoutRequest

with VatlyClient() as vatly:
    checkout = vatly.checkouts.create(
        CreateCheckoutRequest(
            redirect_url_success="https://example.com/success",
            redirect_url_canceled="https://example.com/canceled",
            products=[{"id": "subscription_plan_abc123", "quantity": 1}],
        )
    )
    print(checkout.links.checkout_url.href)
```

```python
from vatly import AsyncVatlyClient


async def read_orders():
    async with AsyncVatlyClient() as vatly:
        async for order in vatly.orders.list_all({"limit": 100}):
            print(order.id, order.total)
```

Pydantic models use snake_case attributes and accept Vatly's camelCase aliases.
Dictionary inputs use **wire-format camelCase keys**. Model requests serialize with
aliases and omit unset fields; explicitly supplied `None` is sent as JSON null.
Money values remain decimal **strings**, never floats.

## Configuration and reliability

```python
from vatly import VatlyClient, RequestOptions

with VatlyClient(timeout=30, max_retries=2) as vatly:
    page = vatly.customers.list({"limit": 25}, options=RequestOptions(timeout=10))
```

Timeouts are **seconds per httpx network phase per attempt**, not a total request deadline;
zero disables timeouts. Default base URL: `https://api.vatly.com/v1`.
`base_url`, `default_headers`, and `transport` (an httpx transport) can be overridden.
`mode` exposes `test` or `live`. Test helpers reject live keys before sending.

POST/PATCH/PUT/DELETE receive a UUID idempotency key, reused across retries.
Set `RequestOptions(idempotency_key="your-operation-id")` to reuse a business-operation key
across separate SDK calls. Set `idempotency_key_generator=None` to disable auto-keys.
GETs and keyed mutations retry 429, 5xx, timeouts and connection errors with exponential
backoff (250ms to 8s plus jitter), honoring numeric or HTTP-date `Retry-After`.
Keyed 409 retries **only** `details.idempotency_outcome == "in_progress"`.
Never blindly retry an `unknown` idempotency outcome: read/reconcile the resource first.
Unkeyed mutations do not retry. Redirects are not followed.

`Vatly-Client-Info` identifies SDK/runtime/OS/architecture. Pass
`client_info={"app": "MyApp/1.0", "framework": "Django/5"}` to add sanitized identifiers,
or `client_info=False` to suppress the SDK-generated header.

## Errors

All API/transport errors extend `VatlyError`, with `status`, `body`, `url`, `method`,
`details`, `errors` and `retry_after`. Network errors retain the httpx exception as `__cause__`.

| Status | Error |
| --- | --- |
| 401 | `VatlyAuthError` |
| 403 | `VatlyForbiddenError` |
| 404 | `VatlyNotFoundError` |
| 409 | `VatlyConflictError` |
| 422 | `VatlyValidationError` |
| 429 | `VatlyRateLimitError` |
| Other / invalid response | `VatlyApiError` |
| Network / timeout | `VatlyConnectionError` / `VatlyTimeoutError` |

```python
from vatly import VatlyValidationError

try:
    # Your API call here
    pass
except VatlyValidationError as error:
    print(error.errors)
```

See [getting started and resource guides](docs/README.md), the generated
[method inventory](docs/API.md), [webhook guide](docs/Webhooks.md), and
[production API reference](https://docs.vatly.com/api-reference).

## Development

Run `.agents/setup` in a fresh orb. It installs uv if missing, provisions Python 3.12,
syncs locked dependencies and runs an import sanity check. Warm runs reuse uv's caches.

```bash
uv run python scripts/generate.py --check
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv build
uv run twine check dist/*
```

See [maintainer notes](docs/Development.md) for spec regeneration, docs sync, and trusted publishing.
