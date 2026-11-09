# Orders

`client.orders` provides read/pagination plus nested refunds and chargebacks.
`create_invoice_update_link(order_id)` returns a hosted billing-details update
link. Financial money values remain decimal strings. Tax and metadata fields are
retained; do not reconstruct invoices from rounded float calculations.

An order line's `product_type` selects what `product_id` refers to. Readers must
support historical `subscription_plan` lines (plan IDs) and `subscription` lines
(subscription IDs). Pending core PR #2910 also stamps initial checkout lines with
the intended subscription ID. An intended ID may temporarily 404 or never resolve
for a skipped trial start: use bounded recovery and inspect status, not ID presence,
before granting access. One-off lines are unaffected.

See [method inventory](API.md#orders) and [order fields](https://docs.vatly.com/api-reference/orders).
