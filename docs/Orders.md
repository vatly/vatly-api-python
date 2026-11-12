# Orders

`client.orders` provides read/pagination plus nested refunds and chargebacks.
`create_invoice_update_link(order_id)` returns a hosted billing-details update
link. Financial money values remain decimal strings. Tax and metadata fields are
retained; do not reconstruct invoices from rounded float calculations.

An order line's `product_type` selects what `product_id` refers to. Readers must
support `subscription_plan` lines (plan IDs) and `subscription` lines
(subscription IDs). Pending [core PR #2910](https://github.com/sandervanhooft/vatlify/pull/2910)
now proposes additive `relatedResources.subscriptionId`, without changing those
product references. This SDK's pinned schema predates that proposal: extra output
fields are preserved, but there is no typed related-resources accessor yet.
Never grant access from an ID alone; verify ownership and subscription status.

See [method inventory](API.md#orders) and [order fields](https://docs.vatly.com/api-reference/orders).
