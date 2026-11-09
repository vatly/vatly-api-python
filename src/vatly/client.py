"""Vatly synchronous and asynchronous clients."""

from . import resources
from ._transport import AsyncTransport, SyncTransport


class VatlyClient(SyncTransport):
    """Resources are initialized lazily and share this client's connection pool."""

    @property
    def checkouts(self) -> resources.Checkouts:
        return resources.Checkouts(self)

    @property
    def customers(self) -> resources.Customers:
        return resources.Customers(self)

    @property
    def one_off_products(self) -> resources.OneOffProducts:
        return resources.OneOffProducts(self)

    @property
    def subscription_plans(self) -> resources.SubscriptionPlans:
        return resources.SubscriptionPlans(self)

    @property
    def orders(self) -> resources.Orders:
        return resources.Orders(self)

    @property
    def refunds(self) -> resources.Refunds:
        return resources.Refunds(self)

    @property
    def chargebacks(self) -> resources.Chargebacks:
        return resources.Chargebacks(self)

    @property
    def webhook_events(self) -> resources.WebhookEvents:
        return resources.WebhookEvents(self)

    @property
    def webhook_endpoints(self) -> resources.WebhookEndpoints:
        return resources.WebhookEndpoints(self)

    @property
    def subscriptions(self) -> resources.Subscriptions:
        return resources.Subscriptions(self)

    @property
    def test_helpers(self) -> resources.TestHelpers:
        return resources.TestHelpers(self)


class AsyncVatlyClient(AsyncTransport):
    """Resources are initialized lazily and share this client's connection pool."""

    @property
    def checkouts(self) -> resources.AsyncCheckouts:
        return resources.AsyncCheckouts(self)

    @property
    def customers(self) -> resources.AsyncCustomers:
        return resources.AsyncCustomers(self)

    @property
    def one_off_products(self) -> resources.AsyncOneOffProducts:
        return resources.AsyncOneOffProducts(self)

    @property
    def subscription_plans(self) -> resources.AsyncSubscriptionPlans:
        return resources.AsyncSubscriptionPlans(self)

    @property
    def orders(self) -> resources.AsyncOrders:
        return resources.AsyncOrders(self)

    @property
    def refunds(self) -> resources.AsyncRefunds:
        return resources.AsyncRefunds(self)

    @property
    def chargebacks(self) -> resources.AsyncChargebacks:
        return resources.AsyncChargebacks(self)

    @property
    def webhook_events(self) -> resources.AsyncWebhookEvents:
        return resources.AsyncWebhookEvents(self)

    @property
    def webhook_endpoints(self) -> resources.AsyncWebhookEndpoints:
        return resources.AsyncWebhookEndpoints(self)

    @property
    def subscriptions(self) -> resources.AsyncSubscriptions:
        return resources.AsyncSubscriptions(self)

    @property
    def test_helpers(self) -> resources.AsyncTestHelpers:
        return resources.AsyncTestHelpers(self)
