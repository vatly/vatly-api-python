# Changelog

## Unreleased

- The `User-Agent` is now a chain of `vendor/package/version` tokens, starting with
  `vatly/vatly-api-python/<version> Python/<version> httpx/<version>` instead of
  `vatly-api-python/<version>`, matching the other Vatly SDKs.
- New `add_version_string()` on both clients: packages and integrations built on the SDK
  append their own token, such as `vatly/vatly-fluent-python/<version>`, so a request
  names every package involved. A `User-Agent` in `default_headers` still replaces it.

## 0.1.0a4 — 2026-11-25

- Sync `openapi.yaml` with the production specification.
- `CreateSubscriptionPlanRequest` and `UpdateSubscriptionPlanRequest` now accept only
  `interval` `"month"` or `"year"` with `interval_count` `1`, matching the API, which
  returns `422` for anything else in live and test mode. On update, send `interval`
  and `interval_count` together. Response models still accept `"day"`, `"week"` and
  higher counts from plans created earlier.
- Request fields the specification marks nullable accept `None`, sent as JSON null and
  treated by Vatly as omitted: checkout `metadata`, `products[].price` and
  `products[].trial_days`, customer `metadata`, refund `metadata`, and subscription
  update `anchor`, among others.
- Requests send only fields the specification defines. Unknown fields, including extra
  attributes on request models, are dropped, and `None` on a field the specification
  does not mark nullable is omitted instead of sent as null.
- Dictionary request bodies are validated through their request model before sending,
  like model inputs. Invalid input raises Pydantic's `ValidationError` without calling
  Vatly, instead of a `VatlyValidationError` from the API.
- `CheckoutProduct.trial_days` must be at least `1` and applies only to subscription
  plans. Omit it or pass `None` for no trial; `0` is rejected.
- Request `metadata` must be an object of string values: at most 50 keys, keys up to 40
  characters, values up to 500 characters.
- Add `Refund.metadata`, on refund resources and in refund webhooks: the metadata sent
  when the refund was created, or `None`.
- Add 14 checkout `locale` values: `cs`, `ca`, `da`, `el`, `fi`, `hu`, `is`, `lt`, `lv`,
  `nb`, `sk`, `sl`, `sv`, `tr`.
- Add one-off product types `digital_download`, `online_course` and `audiobook`.
- Document the `422` for refunding an order that is not a sale.

## 0.1.0a3 — 2026-11-13

- Sync `openapi.yaml` with the production specification.
- Add `OrderLine.related_resources.subscription_id`: the subscription associated with a
  signup, renewal or immediate-update line. `related_resources` is `None` on historical
  and unrelated lines and when omitted; `subscription_id` is `None` on a signup line
  whose subscription is not yet available. `product_type`/`product_id` are unchanged.
- Clarify European positioning, installation and release documentation.

## 0.1.0a2 — 2026-11-12

- Use the PyPI distribution name `vatly-api-python`; imports remain `vatly`.
- Preserve enabled currency/precision intersections in generated Money models.
- Reject empty successful resource responses instead of returning untyped None.
- Include request method and URL in timeout/connection errors in both clients.

## 0.1.0a1 — Unpublished development snapshot

> Alpha — under active development. Every alpha release may include breaking changes. Pin exact versions during alpha.

- Initial typed Python SDK covering all 50 production OpenAPI operations.
- Pydantic models, sync/async httpx clients, cursor iterators, retries, idempotency,
  per-request timeouts, typed errors and raw-body webhook verification.
- Documentation, reproducible code generation, CI, trusted-publishing workflow,
  and cached orb development setup.
