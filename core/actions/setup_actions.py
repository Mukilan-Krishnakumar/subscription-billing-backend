from core.models import Plan
from integrations.stripe.api_client import StripeApiClient


class SetupStripeEntitiesAction:
    def __init__(self):
        self.stripe_api_client = StripeApiClient()

    def execute(self):
        plans = Plan.objects.all()
        for plan in plans:
            plan_name = plan.name
            product = self.stripe_api_client.get_product(product_name=plan_name)
            if not product:
                product = self.stripe_api_client.create_product(product_name=plan_name)
            product_id = product.id
            price_value = plan.price * 100
            currency_value = plan.currency
            interval = plan.billing_cycle
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
            integration_info = plan.integration_info
            stripe_info = integration_info.get("stripe", {})
            stripe_info["product_id"] = product.id
            stripe_info["price_id"] = price.id
            integration_info["stripe"] = stripe_info
            plan.integration_info = integration_info
            plan.save(update_fields=["integration_info"])
