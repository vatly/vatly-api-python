# Getting started

> **Alpha — under active development. Every alpha release may include breaking changes. Pin exact versions during alpha.**

Use `vatly-api-python==0.1.0a2`, imported as `vatly`. Requires Python 3.10+.
Create `VatlyClient` inside `with`, or `AsyncVatlyClient` inside `async with`, to
close the connection pool. Both accept an explicit API key or `VATLY_API_KEY`.
Test and live modes use the same API host; keys select the mode.

See the [SDK README](../README.md) for runnable initialization, checkout,
pagination, retries, configuration, errors and development commands.

| Guide | Purpose |
| --- | --- |
| [API](API.md) | Every method, endpoint and response |
| [Checkouts](Checkouts.md) | Hosted payment pages |
| [Customers](Customers.md) | Customer identity and portal sessions |
| [Subscriptions](Subscriptions.md) | Recurring billing |
| [Subscription Plans](SubscriptionPlans.md) | Subscription catalogue |
| [One-Off Products](OneOffProducts.md) | One-time catalogue |
| [Orders](Orders.md) | Transactions and nested financial operations |
| [Refunds](Refunds.md) | Reversals |
| [Chargebacks](Chargebacks.md) | Disputes |
| [Webhooks](Webhooks.md) | Signatures, events and endpoints |
| [Development](Development.md) | Spec/docs sync, setup, release |
