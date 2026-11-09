# Subscription plans

`client.subscription_plans` provides `list`, `list_all`, `get`, `create`, `update`,
`archive`, and `unarchive`. Use `CreateSubscriptionPlanRequest` and
`UpdateSubscriptionPlanRequest` from `vatly.models`. Money is a decimal string
plus currency; preserve both. Archiving returns `None`, unarchiving the plan.

Test-mode catalogue changes are auto-approved; live changes may await approval.
Archive prevents new sales, not existing subscription renewals. Select
`includeArchived` in dictionary filters when needed, or the corresponding model's
`include_archived` field.

See [method inventory](API.md#subscription_plans) and [plan fields](https://docs.vatly.com/api-reference/subscription-plans).
