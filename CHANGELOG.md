# Changelog

## Unreleased

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
