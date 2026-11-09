"""Generated resource interfaces. Run uv run python scripts/generate.py."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any
from urllib.parse import quote

from . import models
from ._transport import AsyncTransport, RequestOptions, SyncTransport
from .pagination import Page, next_params


class Checkouts:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self,
        params: models.ListCheckoutsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Checkout]:
        """List all checkouts."""
        return self._transport.request(
            "GET", "/checkouts", Page[models.Checkout], body=None, params=params, options=options
        )

    def list_all(
        self,
        params: models.ListCheckoutsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Iterator[models.Checkout]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = self.list(query, options=options)
            yield from page.data
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    def create(
        self,
        body: models.CreateCheckoutRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Checkout:
        """Create a checkout."""
        return self._transport.request(
            "POST", "/checkouts", models.Checkout, body=body, params=None, options=options
        )

    def get(self, checkout_id: str, *, options: RequestOptions | None = None) -> models.Checkout:
        """Get a checkout."""
        return self._transport.request(
            "GET",
            f"/checkouts/{quote(checkout_id, safe='')}",
            models.Checkout,
            body=None,
            params=None,
            options=options,
        )


class AsyncCheckouts:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def list(
        self,
        params: models.ListCheckoutsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Checkout]:
        """List all checkouts."""
        return await self._transport.request(
            "GET", "/checkouts", Page[models.Checkout], body=None, params=params, options=options
        )

    async def list_all(
        self,
        params: models.ListCheckoutsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[models.Checkout]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = await self.list(query, options=options)
            for item in page.data:
                yield item
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    async def create(
        self,
        body: models.CreateCheckoutRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Checkout:
        """Create a checkout."""
        return await self._transport.request(
            "POST", "/checkouts", models.Checkout, body=body, params=None, options=options
        )

    async def get(
        self, checkout_id: str, *, options: RequestOptions | None = None
    ) -> models.Checkout:
        """Get a checkout."""
        return await self._transport.request(
            "GET",
            f"/checkouts/{quote(checkout_id, safe='')}",
            models.Checkout,
            body=None,
            params=None,
            options=options,
        )


class Customers:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self,
        params: models.ListCustomersParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Customer]:
        """List all customers."""
        return self._transport.request(
            "GET", "/customers", Page[models.Customer], body=None, params=params, options=options
        )

    def list_all(
        self,
        params: models.ListCustomersParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Iterator[models.Customer]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = self.list(query, options=options)
            yield from page.data
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    def create(
        self,
        body: models.CreateCustomerRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Customer:
        """Create a customer."""
        return self._transport.request(
            "POST", "/customers", models.Customer, body=body, params=None, options=options
        )

    def get(self, customer_id: str, *, options: RequestOptions | None = None) -> models.Customer:
        """Get a customer."""
        return self._transport.request(
            "GET",
            f"/customers/{quote(customer_id, safe='')}",
            models.Customer,
            body=None,
            params=None,
            options=options,
        )

    def update(
        self,
        customer_id: str,
        body: models.UpdateCustomerRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Customer:
        """Update a customer."""
        return self._transport.request(
            "PATCH",
            f"/customers/{quote(customer_id, safe='')}",
            models.Customer,
            body=body,
            params=None,
            options=options,
        )

    def create_portal_session(
        self,
        customer_id: str,
        body: models.CreatePortalSessionRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.PortalSession:
        """Create a hosted customer portal session."""
        return self._transport.request(
            "POST",
            f"/customers/{quote(customer_id, safe='')}/portal-sessions",
            models.PortalSession,
            body=body,
            params=None,
            options=options,
        )

    def list_subscriptions(
        self,
        customer_id: str,
        params: models.ListCustomerSubscriptionsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Subscription]:
        """List customer subscriptions."""
        return self._transport.request(
            "GET",
            f"/customers/{quote(customer_id, safe='')}/subscriptions",
            Page[models.Subscription],
            body=None,
            params=params,
            options=options,
        )

    def list_all_subscriptions(
        self,
        customer_id: str,
        params: models.ListCustomerSubscriptionsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Iterator[models.Subscription]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = self.list_subscriptions(customer_id, query, options=options)
            yield from page.data
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    def get_subscription(
        self, customer_id: str, subscription_id: str, *, options: RequestOptions | None = None
    ) -> models.Subscription:
        """Get a customer subscription."""
        return self._transport.request(
            "GET",
            f"/customers/{quote(customer_id, safe='')}/subscriptions/{quote(subscription_id, safe='')}",
            models.Subscription,
            body=None,
            params=None,
            options=options,
        )


class AsyncCustomers:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def list(
        self,
        params: models.ListCustomersParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Customer]:
        """List all customers."""
        return await self._transport.request(
            "GET", "/customers", Page[models.Customer], body=None, params=params, options=options
        )

    async def list_all(
        self,
        params: models.ListCustomersParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[models.Customer]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = await self.list(query, options=options)
            for item in page.data:
                yield item
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    async def create(
        self,
        body: models.CreateCustomerRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Customer:
        """Create a customer."""
        return await self._transport.request(
            "POST", "/customers", models.Customer, body=body, params=None, options=options
        )

    async def get(
        self, customer_id: str, *, options: RequestOptions | None = None
    ) -> models.Customer:
        """Get a customer."""
        return await self._transport.request(
            "GET",
            f"/customers/{quote(customer_id, safe='')}",
            models.Customer,
            body=None,
            params=None,
            options=options,
        )

    async def update(
        self,
        customer_id: str,
        body: models.UpdateCustomerRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Customer:
        """Update a customer."""
        return await self._transport.request(
            "PATCH",
            f"/customers/{quote(customer_id, safe='')}",
            models.Customer,
            body=body,
            params=None,
            options=options,
        )

    async def create_portal_session(
        self,
        customer_id: str,
        body: models.CreatePortalSessionRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.PortalSession:
        """Create a hosted customer portal session."""
        return await self._transport.request(
            "POST",
            f"/customers/{quote(customer_id, safe='')}/portal-sessions",
            models.PortalSession,
            body=body,
            params=None,
            options=options,
        )

    async def list_subscriptions(
        self,
        customer_id: str,
        params: models.ListCustomerSubscriptionsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Subscription]:
        """List customer subscriptions."""
        return await self._transport.request(
            "GET",
            f"/customers/{quote(customer_id, safe='')}/subscriptions",
            Page[models.Subscription],
            body=None,
            params=params,
            options=options,
        )

    async def list_all_subscriptions(
        self,
        customer_id: str,
        params: models.ListCustomerSubscriptionsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[models.Subscription]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = await self.list_subscriptions(customer_id, query, options=options)
            for item in page.data:
                yield item
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    async def get_subscription(
        self, customer_id: str, subscription_id: str, *, options: RequestOptions | None = None
    ) -> models.Subscription:
        """Get a customer subscription."""
        return await self._transport.request(
            "GET",
            f"/customers/{quote(customer_id, safe='')}/subscriptions/{quote(subscription_id, safe='')}",
            models.Subscription,
            body=None,
            params=None,
            options=options,
        )


class OneOffProducts:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self,
        params: models.ListOneOffProductsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.OneOffProduct]:
        """List all one-off products."""
        return self._transport.request(
            "GET",
            "/one-off-products",
            Page[models.OneOffProduct],
            body=None,
            params=params,
            options=options,
        )

    def list_all(
        self,
        params: models.ListOneOffProductsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Iterator[models.OneOffProduct]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = self.list(query, options=options)
            yield from page.data
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    def create(
        self,
        body: models.CreateOneOffProductRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.OneOffProduct:
        """Create a one-off product."""
        return self._transport.request(
            "POST",
            "/one-off-products",
            models.OneOffProduct,
            body=body,
            params=None,
            options=options,
        )

    def get(
        self, one_off_product_id: str, *, options: RequestOptions | None = None
    ) -> models.OneOffProduct:
        """Get a one-off product."""
        return self._transport.request(
            "GET",
            f"/one-off-products/{quote(one_off_product_id, safe='')}",
            models.OneOffProduct,
            body=None,
            params=None,
            options=options,
        )

    def update(
        self,
        one_off_product_id: str,
        body: models.UpdateOneOffProductRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.OneOffProduct:
        """Request an update to a one-off product."""
        return self._transport.request(
            "PATCH",
            f"/one-off-products/{quote(one_off_product_id, safe='')}",
            models.OneOffProduct,
            body=body,
            params=None,
            options=options,
        )

    def archive(self, one_off_product_id: str, *, options: RequestOptions | None = None) -> None:
        """Archive a one-off product."""
        return self._transport.request(
            "POST",
            f"/one-off-products/{quote(one_off_product_id, safe='')}/archive",
            type(None),
            body=None,
            params=None,
            options=options,
        )

    def unarchive(
        self, one_off_product_id: str, *, options: RequestOptions | None = None
    ) -> models.OneOffProduct:
        """Unarchive a one-off product."""
        return self._transport.request(
            "DELETE",
            f"/one-off-products/{quote(one_off_product_id, safe='')}/archive",
            models.OneOffProduct,
            body=None,
            params=None,
            options=options,
        )


class AsyncOneOffProducts:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def list(
        self,
        params: models.ListOneOffProductsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.OneOffProduct]:
        """List all one-off products."""
        return await self._transport.request(
            "GET",
            "/one-off-products",
            Page[models.OneOffProduct],
            body=None,
            params=params,
            options=options,
        )

    async def list_all(
        self,
        params: models.ListOneOffProductsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[models.OneOffProduct]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = await self.list(query, options=options)
            for item in page.data:
                yield item
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    async def create(
        self,
        body: models.CreateOneOffProductRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.OneOffProduct:
        """Create a one-off product."""
        return await self._transport.request(
            "POST",
            "/one-off-products",
            models.OneOffProduct,
            body=body,
            params=None,
            options=options,
        )

    async def get(
        self, one_off_product_id: str, *, options: RequestOptions | None = None
    ) -> models.OneOffProduct:
        """Get a one-off product."""
        return await self._transport.request(
            "GET",
            f"/one-off-products/{quote(one_off_product_id, safe='')}",
            models.OneOffProduct,
            body=None,
            params=None,
            options=options,
        )

    async def update(
        self,
        one_off_product_id: str,
        body: models.UpdateOneOffProductRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.OneOffProduct:
        """Request an update to a one-off product."""
        return await self._transport.request(
            "PATCH",
            f"/one-off-products/{quote(one_off_product_id, safe='')}",
            models.OneOffProduct,
            body=body,
            params=None,
            options=options,
        )

    async def archive(
        self, one_off_product_id: str, *, options: RequestOptions | None = None
    ) -> None:
        """Archive a one-off product."""
        return await self._transport.request(
            "POST",
            f"/one-off-products/{quote(one_off_product_id, safe='')}/archive",
            type(None),
            body=None,
            params=None,
            options=options,
        )

    async def unarchive(
        self, one_off_product_id: str, *, options: RequestOptions | None = None
    ) -> models.OneOffProduct:
        """Unarchive a one-off product."""
        return await self._transport.request(
            "DELETE",
            f"/one-off-products/{quote(one_off_product_id, safe='')}/archive",
            models.OneOffProduct,
            body=None,
            params=None,
            options=options,
        )


class SubscriptionPlans:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self,
        params: models.ListSubscriptionPlansParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.SubscriptionPlan]:
        """List all subscription plans."""
        return self._transport.request(
            "GET",
            "/subscription-plans",
            Page[models.SubscriptionPlan],
            body=None,
            params=params,
            options=options,
        )

    def list_all(
        self,
        params: models.ListSubscriptionPlansParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Iterator[models.SubscriptionPlan]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = self.list(query, options=options)
            yield from page.data
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    def create(
        self,
        body: models.CreateSubscriptionPlanRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.SubscriptionPlan:
        """Create a subscription plan."""
        return self._transport.request(
            "POST",
            "/subscription-plans",
            models.SubscriptionPlan,
            body=body,
            params=None,
            options=options,
        )

    def get(
        self, subscription_plan_id: str, *, options: RequestOptions | None = None
    ) -> models.SubscriptionPlan:
        """Get a subscription plan."""
        return self._transport.request(
            "GET",
            f"/subscription-plans/{quote(subscription_plan_id, safe='')}",
            models.SubscriptionPlan,
            body=None,
            params=None,
            options=options,
        )

    def update(
        self,
        subscription_plan_id: str,
        body: models.UpdateSubscriptionPlanRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.SubscriptionPlan:
        """Request an update to a subscription plan."""
        return self._transport.request(
            "PATCH",
            f"/subscription-plans/{quote(subscription_plan_id, safe='')}",
            models.SubscriptionPlan,
            body=body,
            params=None,
            options=options,
        )

    def archive(self, subscription_plan_id: str, *, options: RequestOptions | None = None) -> None:
        """Archive a subscription plan."""
        return self._transport.request(
            "POST",
            f"/subscription-plans/{quote(subscription_plan_id, safe='')}/archive",
            type(None),
            body=None,
            params=None,
            options=options,
        )

    def unarchive(
        self, subscription_plan_id: str, *, options: RequestOptions | None = None
    ) -> models.SubscriptionPlan:
        """Unarchive a subscription plan."""
        return self._transport.request(
            "DELETE",
            f"/subscription-plans/{quote(subscription_plan_id, safe='')}/archive",
            models.SubscriptionPlan,
            body=None,
            params=None,
            options=options,
        )


class AsyncSubscriptionPlans:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def list(
        self,
        params: models.ListSubscriptionPlansParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.SubscriptionPlan]:
        """List all subscription plans."""
        return await self._transport.request(
            "GET",
            "/subscription-plans",
            Page[models.SubscriptionPlan],
            body=None,
            params=params,
            options=options,
        )

    async def list_all(
        self,
        params: models.ListSubscriptionPlansParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[models.SubscriptionPlan]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = await self.list(query, options=options)
            for item in page.data:
                yield item
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    async def create(
        self,
        body: models.CreateSubscriptionPlanRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.SubscriptionPlan:
        """Create a subscription plan."""
        return await self._transport.request(
            "POST",
            "/subscription-plans",
            models.SubscriptionPlan,
            body=body,
            params=None,
            options=options,
        )

    async def get(
        self, subscription_plan_id: str, *, options: RequestOptions | None = None
    ) -> models.SubscriptionPlan:
        """Get a subscription plan."""
        return await self._transport.request(
            "GET",
            f"/subscription-plans/{quote(subscription_plan_id, safe='')}",
            models.SubscriptionPlan,
            body=None,
            params=None,
            options=options,
        )

    async def update(
        self,
        subscription_plan_id: str,
        body: models.UpdateSubscriptionPlanRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.SubscriptionPlan:
        """Request an update to a subscription plan."""
        return await self._transport.request(
            "PATCH",
            f"/subscription-plans/{quote(subscription_plan_id, safe='')}",
            models.SubscriptionPlan,
            body=body,
            params=None,
            options=options,
        )

    async def archive(
        self, subscription_plan_id: str, *, options: RequestOptions | None = None
    ) -> None:
        """Archive a subscription plan."""
        return await self._transport.request(
            "POST",
            f"/subscription-plans/{quote(subscription_plan_id, safe='')}/archive",
            type(None),
            body=None,
            params=None,
            options=options,
        )

    async def unarchive(
        self, subscription_plan_id: str, *, options: RequestOptions | None = None
    ) -> models.SubscriptionPlan:
        """Unarchive a subscription plan."""
        return await self._transport.request(
            "DELETE",
            f"/subscription-plans/{quote(subscription_plan_id, safe='')}/archive",
            models.SubscriptionPlan,
            body=None,
            params=None,
            options=options,
        )


class Orders:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self,
        params: models.ListOrdersParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Order]:
        """List all orders."""
        return self._transport.request(
            "GET", "/orders", Page[models.Order], body=None, params=params, options=options
        )

    def list_all(
        self,
        params: models.ListOrdersParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Iterator[models.Order]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = self.list(query, options=options)
            yield from page.data
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    def get(self, order_id: str, *, options: RequestOptions | None = None) -> models.Order:
        """Get an order."""
        return self._transport.request(
            "GET",
            f"/orders/{quote(order_id, safe='')}",
            models.Order,
            body=None,
            params=None,
            options=options,
        )

    def create_invoice_update_link(
        self, order_id: str, *, options: RequestOptions | None = None
    ) -> models.InvoiceUpdateLink:
        """Create invoice update link."""
        return self._transport.request(
            "POST",
            f"/orders/{quote(order_id, safe='')}/invoice-update-link",
            models.InvoiceUpdateLink,
            body=None,
            params=None,
            options=options,
        )

    def list_refunds(
        self,
        order_id: str,
        params: models.ListOrderRefundsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Refund]:
        """List order refunds."""
        return self._transport.request(
            "GET",
            f"/orders/{quote(order_id, safe='')}/refunds",
            Page[models.Refund],
            body=None,
            params=params,
            options=options,
        )

    def list_all_refunds(
        self,
        order_id: str,
        params: models.ListOrderRefundsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Iterator[models.Refund]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = self.list_refunds(order_id, query, options=options)
            yield from page.data
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    def create_refund(
        self,
        order_id: str,
        body: models.CreateRefundRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Refund:
        """Create a partial refund."""
        return self._transport.request(
            "POST",
            f"/orders/{quote(order_id, safe='')}/refunds",
            models.Refund,
            body=body,
            params=None,
            options=options,
        )

    def create_full_refund(
        self,
        order_id: str,
        body: models.CreateFullRefundRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Refund:
        """Create a full refund."""
        return self._transport.request(
            "POST",
            f"/orders/{quote(order_id, safe='')}/refunds/full",
            models.Refund,
            body=body,
            params=None,
            options=options,
        )

    def get_refund(
        self, order_id: str, refund_id: str, *, options: RequestOptions | None = None
    ) -> models.Refund:
        """Get an order refund."""
        return self._transport.request(
            "GET",
            f"/orders/{quote(order_id, safe='')}/refunds/{quote(refund_id, safe='')}",
            models.Refund,
            body=None,
            params=None,
            options=options,
        )

    def cancel_refund(
        self, order_id: str, refund_id: str, *, options: RequestOptions | None = None
    ) -> None:
        """Cancel a refund."""
        return self._transport.request(
            "DELETE",
            f"/orders/{quote(order_id, safe='')}/refunds/{quote(refund_id, safe='')}",
            type(None),
            body=None,
            params=None,
            options=options,
        )

    def list_chargebacks(
        self,
        order_id: str,
        params: models.ListOrderChargebacksParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Chargeback]:
        """List order chargebacks."""
        return self._transport.request(
            "GET",
            f"/orders/{quote(order_id, safe='')}/chargebacks",
            Page[models.Chargeback],
            body=None,
            params=params,
            options=options,
        )

    def list_all_chargebacks(
        self,
        order_id: str,
        params: models.ListOrderChargebacksParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Iterator[models.Chargeback]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = self.list_chargebacks(order_id, query, options=options)
            yield from page.data
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    def get_chargeback(
        self, order_id: str, chargeback_id: str, *, options: RequestOptions | None = None
    ) -> models.Chargeback:
        """Get an order chargeback."""
        return self._transport.request(
            "GET",
            f"/orders/{quote(order_id, safe='')}/chargebacks/{quote(chargeback_id, safe='')}",
            models.Chargeback,
            body=None,
            params=None,
            options=options,
        )


class AsyncOrders:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def list(
        self,
        params: models.ListOrdersParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Order]:
        """List all orders."""
        return await self._transport.request(
            "GET", "/orders", Page[models.Order], body=None, params=params, options=options
        )

    async def list_all(
        self,
        params: models.ListOrdersParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[models.Order]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = await self.list(query, options=options)
            for item in page.data:
                yield item
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    async def get(self, order_id: str, *, options: RequestOptions | None = None) -> models.Order:
        """Get an order."""
        return await self._transport.request(
            "GET",
            f"/orders/{quote(order_id, safe='')}",
            models.Order,
            body=None,
            params=None,
            options=options,
        )

    async def create_invoice_update_link(
        self, order_id: str, *, options: RequestOptions | None = None
    ) -> models.InvoiceUpdateLink:
        """Create invoice update link."""
        return await self._transport.request(
            "POST",
            f"/orders/{quote(order_id, safe='')}/invoice-update-link",
            models.InvoiceUpdateLink,
            body=None,
            params=None,
            options=options,
        )

    async def list_refunds(
        self,
        order_id: str,
        params: models.ListOrderRefundsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Refund]:
        """List order refunds."""
        return await self._transport.request(
            "GET",
            f"/orders/{quote(order_id, safe='')}/refunds",
            Page[models.Refund],
            body=None,
            params=params,
            options=options,
        )

    async def list_all_refunds(
        self,
        order_id: str,
        params: models.ListOrderRefundsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[models.Refund]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = await self.list_refunds(order_id, query, options=options)
            for item in page.data:
                yield item
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    async def create_refund(
        self,
        order_id: str,
        body: models.CreateRefundRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Refund:
        """Create a partial refund."""
        return await self._transport.request(
            "POST",
            f"/orders/{quote(order_id, safe='')}/refunds",
            models.Refund,
            body=body,
            params=None,
            options=options,
        )

    async def create_full_refund(
        self,
        order_id: str,
        body: models.CreateFullRefundRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Refund:
        """Create a full refund."""
        return await self._transport.request(
            "POST",
            f"/orders/{quote(order_id, safe='')}/refunds/full",
            models.Refund,
            body=body,
            params=None,
            options=options,
        )

    async def get_refund(
        self, order_id: str, refund_id: str, *, options: RequestOptions | None = None
    ) -> models.Refund:
        """Get an order refund."""
        return await self._transport.request(
            "GET",
            f"/orders/{quote(order_id, safe='')}/refunds/{quote(refund_id, safe='')}",
            models.Refund,
            body=None,
            params=None,
            options=options,
        )

    async def cancel_refund(
        self, order_id: str, refund_id: str, *, options: RequestOptions | None = None
    ) -> None:
        """Cancel a refund."""
        return await self._transport.request(
            "DELETE",
            f"/orders/{quote(order_id, safe='')}/refunds/{quote(refund_id, safe='')}",
            type(None),
            body=None,
            params=None,
            options=options,
        )

    async def list_chargebacks(
        self,
        order_id: str,
        params: models.ListOrderChargebacksParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Chargeback]:
        """List order chargebacks."""
        return await self._transport.request(
            "GET",
            f"/orders/{quote(order_id, safe='')}/chargebacks",
            Page[models.Chargeback],
            body=None,
            params=params,
            options=options,
        )

    async def list_all_chargebacks(
        self,
        order_id: str,
        params: models.ListOrderChargebacksParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[models.Chargeback]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = await self.list_chargebacks(order_id, query, options=options)
            for item in page.data:
                yield item
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    async def get_chargeback(
        self, order_id: str, chargeback_id: str, *, options: RequestOptions | None = None
    ) -> models.Chargeback:
        """Get an order chargeback."""
        return await self._transport.request(
            "GET",
            f"/orders/{quote(order_id, safe='')}/chargebacks/{quote(chargeback_id, safe='')}",
            models.Chargeback,
            body=None,
            params=None,
            options=options,
        )


class Refunds:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self,
        params: models.ListRefundsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Refund]:
        """List all refunds."""
        return self._transport.request(
            "GET", "/refunds", Page[models.Refund], body=None, params=params, options=options
        )

    def list_all(
        self,
        params: models.ListRefundsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Iterator[models.Refund]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = self.list(query, options=options)
            yield from page.data
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    def get(self, refund_id: str, *, options: RequestOptions | None = None) -> models.Refund:
        """Get a refund."""
        return self._transport.request(
            "GET",
            f"/refunds/{quote(refund_id, safe='')}",
            models.Refund,
            body=None,
            params=None,
            options=options,
        )


class AsyncRefunds:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def list(
        self,
        params: models.ListRefundsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Refund]:
        """List all refunds."""
        return await self._transport.request(
            "GET", "/refunds", Page[models.Refund], body=None, params=params, options=options
        )

    async def list_all(
        self,
        params: models.ListRefundsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[models.Refund]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = await self.list(query, options=options)
            for item in page.data:
                yield item
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    async def get(self, refund_id: str, *, options: RequestOptions | None = None) -> models.Refund:
        """Get a refund."""
        return await self._transport.request(
            "GET",
            f"/refunds/{quote(refund_id, safe='')}",
            models.Refund,
            body=None,
            params=None,
            options=options,
        )


class Chargebacks:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self,
        params: models.ListChargebacksParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Chargeback]:
        """List all chargebacks."""
        return self._transport.request(
            "GET",
            "/chargebacks",
            Page[models.Chargeback],
            body=None,
            params=params,
            options=options,
        )

    def list_all(
        self,
        params: models.ListChargebacksParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Iterator[models.Chargeback]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = self.list(query, options=options)
            yield from page.data
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    def get(
        self, chargeback_id: str, *, options: RequestOptions | None = None
    ) -> models.Chargeback:
        """Get a chargeback."""
        return self._transport.request(
            "GET",
            f"/chargebacks/{quote(chargeback_id, safe='')}",
            models.Chargeback,
            body=None,
            params=None,
            options=options,
        )


class AsyncChargebacks:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def list(
        self,
        params: models.ListChargebacksParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Chargeback]:
        """List all chargebacks."""
        return await self._transport.request(
            "GET",
            "/chargebacks",
            Page[models.Chargeback],
            body=None,
            params=params,
            options=options,
        )

    async def list_all(
        self,
        params: models.ListChargebacksParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[models.Chargeback]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = await self.list(query, options=options)
            for item in page.data:
                yield item
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    async def get(
        self, chargeback_id: str, *, options: RequestOptions | None = None
    ) -> models.Chargeback:
        """Get a chargeback."""
        return await self._transport.request(
            "GET",
            f"/chargebacks/{quote(chargeback_id, safe='')}",
            models.Chargeback,
            body=None,
            params=None,
            options=options,
        )


class WebhookEvents:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def get(self, event_id: str, *, options: RequestOptions | None = None) -> models.WebhookEvent:
        """Get webhook event."""
        return self._transport.request(
            "GET",
            f"/webhook-events/{quote(event_id, safe='')}",
            models.WebhookEvent,
            body=None,
            params=None,
            options=options,
        )


class AsyncWebhookEvents:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def get(
        self, event_id: str, *, options: RequestOptions | None = None
    ) -> models.WebhookEvent:
        """Get webhook event."""
        return await self._transport.request(
            "GET",
            f"/webhook-events/{quote(event_id, safe='')}",
            models.WebhookEvent,
            body=None,
            params=None,
            options=options,
        )


class WebhookEndpoints:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self,
        params: models.ListWebhookEndpointsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.WebhookEndpoint]:
        """List webhook endpoints."""
        return self._transport.request(
            "GET",
            "/webhook-endpoints",
            Page[models.WebhookEndpoint],
            body=None,
            params=params,
            options=options,
        )

    def list_all(
        self,
        params: models.ListWebhookEndpointsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Iterator[models.WebhookEndpoint]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = self.list(query, options=options)
            yield from page.data
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    def create(
        self,
        body: models.CreateWebhookEndpointRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.WebhookEndpoint:
        """Register a webhook endpoint."""
        return self._transport.request(
            "POST",
            "/webhook-endpoints",
            models.WebhookEndpoint,
            body=body,
            params=None,
            options=options,
        )

    def get(
        self, webhook_endpoint_id: str, *, options: RequestOptions | None = None
    ) -> models.WebhookEndpoint:
        """Get a webhook endpoint."""
        return self._transport.request(
            "GET",
            f"/webhook-endpoints/{quote(webhook_endpoint_id, safe='')}",
            models.WebhookEndpoint,
            body=None,
            params=None,
            options=options,
        )

    def update(
        self,
        webhook_endpoint_id: str,
        body: models.UpdateWebhookEndpointRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.WebhookEndpoint:
        """Update a webhook endpoint."""
        return self._transport.request(
            "PATCH",
            f"/webhook-endpoints/{quote(webhook_endpoint_id, safe='')}",
            models.WebhookEndpoint,
            body=body,
            params=None,
            options=options,
        )

    def delete(self, webhook_endpoint_id: str, *, options: RequestOptions | None = None) -> None:
        """Delete a webhook endpoint."""
        return self._transport.request(
            "DELETE",
            f"/webhook-endpoints/{quote(webhook_endpoint_id, safe='')}",
            type(None),
            body=None,
            params=None,
            options=options,
        )


class AsyncWebhookEndpoints:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def list(
        self,
        params: models.ListWebhookEndpointsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.WebhookEndpoint]:
        """List webhook endpoints."""
        return await self._transport.request(
            "GET",
            "/webhook-endpoints",
            Page[models.WebhookEndpoint],
            body=None,
            params=params,
            options=options,
        )

    async def list_all(
        self,
        params: models.ListWebhookEndpointsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[models.WebhookEndpoint]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = await self.list(query, options=options)
            for item in page.data:
                yield item
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    async def create(
        self,
        body: models.CreateWebhookEndpointRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.WebhookEndpoint:
        """Register a webhook endpoint."""
        return await self._transport.request(
            "POST",
            "/webhook-endpoints",
            models.WebhookEndpoint,
            body=body,
            params=None,
            options=options,
        )

    async def get(
        self, webhook_endpoint_id: str, *, options: RequestOptions | None = None
    ) -> models.WebhookEndpoint:
        """Get a webhook endpoint."""
        return await self._transport.request(
            "GET",
            f"/webhook-endpoints/{quote(webhook_endpoint_id, safe='')}",
            models.WebhookEndpoint,
            body=None,
            params=None,
            options=options,
        )

    async def update(
        self,
        webhook_endpoint_id: str,
        body: models.UpdateWebhookEndpointRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.WebhookEndpoint:
        """Update a webhook endpoint."""
        return await self._transport.request(
            "PATCH",
            f"/webhook-endpoints/{quote(webhook_endpoint_id, safe='')}",
            models.WebhookEndpoint,
            body=body,
            params=None,
            options=options,
        )

    async def delete(
        self, webhook_endpoint_id: str, *, options: RequestOptions | None = None
    ) -> None:
        """Delete a webhook endpoint."""
        return await self._transport.request(
            "DELETE",
            f"/webhook-endpoints/{quote(webhook_endpoint_id, safe='')}",
            type(None),
            body=None,
            params=None,
            options=options,
        )


class Subscriptions:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def list(
        self,
        params: models.ListSubscriptionsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Subscription]:
        """List all subscriptions."""
        return self._transport.request(
            "GET",
            "/subscriptions",
            Page[models.Subscription],
            body=None,
            params=params,
            options=options,
        )

    def list_all(
        self,
        params: models.ListSubscriptionsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Iterator[models.Subscription]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = self.list(query, options=options)
            yield from page.data
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    def get(
        self, subscription_id: str, *, options: RequestOptions | None = None
    ) -> models.Subscription:
        """Get a subscription."""
        return self._transport.request(
            "GET",
            f"/subscriptions/{quote(subscription_id, safe='')}",
            models.Subscription,
            body=None,
            params=None,
            options=options,
        )

    def update(
        self,
        subscription_id: str,
        body: models.UpdateSubscriptionRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Subscription:
        """Update a subscription."""
        return self._transport.request(
            "PATCH",
            f"/subscriptions/{quote(subscription_id, safe='')}",
            models.Subscription,
            body=body,
            params=None,
            options=options,
        )

    def cancel(
        self,
        subscription_id: str,
        params: models.CancelSubscriptionParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> None:
        """Cancel a subscription."""
        return self._transport.request(
            "DELETE",
            f"/subscriptions/{quote(subscription_id, safe='')}",
            type(None),
            body=None,
            params=params,
            options=options,
        )

    def create_billing_update_link(
        self,
        subscription_id: str,
        body: models.UpdateSubscriptionBillingRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.CreateSubscriptionBillingUpdateLinkResponse:
        """Create billing update link."""
        return self._transport.request(
            "POST",
            f"/subscriptions/{quote(subscription_id, safe='')}/billing-update-link",
            models.CreateSubscriptionBillingUpdateLinkResponse,
            body=body,
            params=None,
            options=options,
        )

    def resume(
        self, subscription_id: str, *, options: RequestOptions | None = None
    ) -> models.Subscription:
        """Resume a canceled subscription."""
        return self._transport.request(
            "POST",
            f"/subscriptions/{quote(subscription_id, safe='')}/resume",
            models.Subscription,
            body=None,
            params=None,
            options=options,
        )


class AsyncSubscriptions:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def list(
        self,
        params: models.ListSubscriptionsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> Page[models.Subscription]:
        """List all subscriptions."""
        return await self._transport.request(
            "GET",
            "/subscriptions",
            Page[models.Subscription],
            body=None,
            params=params,
            options=options,
        )

    async def list_all(
        self,
        params: models.ListSubscriptionsParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[models.Subscription]:
        query = self._transport.serialize(params) or {}
        seen: set[str] = set()
        if query.get("startingAfter"):
            seen.add(str(query["startingAfter"]))
        while True:
            page = await self.list(query, options=options)
            for item in page.data:
                yield item
            following = next_params(page, query, seen)
            if following is None:
                return
            query = following

    async def get(
        self, subscription_id: str, *, options: RequestOptions | None = None
    ) -> models.Subscription:
        """Get a subscription."""
        return await self._transport.request(
            "GET",
            f"/subscriptions/{quote(subscription_id, safe='')}",
            models.Subscription,
            body=None,
            params=None,
            options=options,
        )

    async def update(
        self,
        subscription_id: str,
        body: models.UpdateSubscriptionRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Subscription:
        """Update a subscription."""
        return await self._transport.request(
            "PATCH",
            f"/subscriptions/{quote(subscription_id, safe='')}",
            models.Subscription,
            body=body,
            params=None,
            options=options,
        )

    async def cancel(
        self,
        subscription_id: str,
        params: models.CancelSubscriptionParams | dict[str, Any] | None = None,
        *,
        options: RequestOptions | None = None,
    ) -> None:
        """Cancel a subscription."""
        return await self._transport.request(
            "DELETE",
            f"/subscriptions/{quote(subscription_id, safe='')}",
            type(None),
            body=None,
            params=params,
            options=options,
        )

    async def create_billing_update_link(
        self,
        subscription_id: str,
        body: models.UpdateSubscriptionBillingRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.CreateSubscriptionBillingUpdateLinkResponse:
        """Create billing update link."""
        return await self._transport.request(
            "POST",
            f"/subscriptions/{quote(subscription_id, safe='')}/billing-update-link",
            models.CreateSubscriptionBillingUpdateLinkResponse,
            body=body,
            params=None,
            options=options,
        )

    async def resume(
        self, subscription_id: str, *, options: RequestOptions | None = None
    ) -> models.Subscription:
        """Resume a canceled subscription."""
        return await self._transport.request(
            "POST",
            f"/subscriptions/{quote(subscription_id, safe='')}/resume",
            models.Subscription,
            body=None,
            params=None,
            options=options,
        )


class TestHelpers:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def fast_forward_renewal(
        self,
        subscription_id: str,
        body: models.FastForwardSubscriptionRenewalRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Subscription:
        """Fast-forward subscription renewal."""
        if self._transport.mode != "test":
            raise ValueError("Test helpers require a test-mode API key")
        return self._transport.request(
            "POST",
            f"/test-helpers/subscriptions/{quote(subscription_id, safe='')}/fast-forward-renewal",
            models.Subscription,
            body=body,
            params=None,
            options=options,
        )

    def simulate_order_payment(
        self,
        order_id: str,
        body: models.SimulateOrderPaymentRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Order:
        """Simulate an order payment outcome."""
        if self._transport.mode != "test":
            raise ValueError("Test helpers require a test-mode API key")
        return self._transport.request(
            "POST",
            f"/test-helpers/orders/{quote(order_id, safe='')}/simulate-payment",
            models.Order,
            body=body,
            params=None,
            options=options,
        )


class AsyncTestHelpers:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def fast_forward_renewal(
        self,
        subscription_id: str,
        body: models.FastForwardSubscriptionRenewalRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Subscription:
        """Fast-forward subscription renewal."""
        if self._transport.mode != "test":
            raise ValueError("Test helpers require a test-mode API key")
        return await self._transport.request(
            "POST",
            f"/test-helpers/subscriptions/{quote(subscription_id, safe='')}/fast-forward-renewal",
            models.Subscription,
            body=body,
            params=None,
            options=options,
        )

    async def simulate_order_payment(
        self,
        order_id: str,
        body: models.SimulateOrderPaymentRequest | dict[str, Any],
        *,
        options: RequestOptions | None = None,
    ) -> models.Order:
        """Simulate an order payment outcome."""
        if self._transport.mode != "test":
            raise ValueError("Test helpers require a test-mode API key")
        return await self._transport.request(
            "POST",
            f"/test-helpers/orders/{quote(order_id, safe='')}/simulate-payment",
            models.Order,
            body=body,
            params=None,
            options=options,
        )
