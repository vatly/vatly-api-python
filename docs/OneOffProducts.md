# One-off products

`client.one_off_products` provides `list`, `list_all`, `get`, `create`, `update`,
`archive`, and `unarchive`. Use `CreateOneOffProductRequest` and
`UpdateOneOffProductRequest` from `vatly.models`. `archive` returns `None`;
`unarchive` returns the resource. Mode and approval behavior follow the API key.

The output `product_type` preserves catalogue strings not yet listed in the
production spec (including observed `digital_download`). Request validation still
follows the production request schema. Unknown response fields are preserved.

See [method inventory](API.md#one_off_products) and [product fields](https://docs.vatly.com/api-reference/one-off-products).
