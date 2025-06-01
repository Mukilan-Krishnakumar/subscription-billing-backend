import logging

from core.models import Plan

from integrations.stripe.api_client import StripeApiClient


class SetupStripeEntitiesAction:
    def __init__(self):
        self.stripe_api_client = StripeApiClient()
        self.logger = logging.getLogger(__name__)

    def get_or_create_product(self, product_name):
        product = self.stripe_api_client.get_product(product_name=product_name)
        if not product:
            product = self.stripe_api_client.create_product(product_name=product_name)
        return product

    def get_or_create_pricing(
        self,
        price_value,
        currency_value,
        product_id,
        interval=Plan.BillingCycle.MONTHLY,
    ):
        price = self.stripe_api_client.get_pricing(
            price_value=price_value,
            currency_value=currency_value,
            product_id=product_id,
        )
        if not price:
            price = self.stripe_api_client.create_pricing(
                price_value=price_value,
                currency_value=currency_value,
                interval=interval,
                product_id=product_id,
            )
        return price

    def execute(self):
        plans = Plan.objects.all()
        for plan in plans:
            try:
                plan_name = plan.name
                product = self.get_or_create_product(product_name=plan_name)

                product_id = product.id
                price_value = plan.price * 100
                currency_value = plan.currency
                interval = plan.billing_cycle
                price = self.get_or_create_pricing(
                    price_value=price_value,
                    currency_value=currency_value,
                    product_id=product_id,
                    interval=interval,
                )

                integration_info = plan.integration_info
                stripe_info = integration_info.get("stripe", {})
                stripe_info["product_id"] = product.id
                stripe_info["price_id"] = price.id
                integration_info["stripe"] = stripe_info
                plan.integration_info = integration_info

                plan.save(update_fields=["integration_info"])
            except Exception:
                self.logger.exception(
                    "Exception faced when created stripe entities for plan with id %s",
                    plan.id,
                )
