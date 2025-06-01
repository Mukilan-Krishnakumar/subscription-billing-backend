import logging
from django.conf import settings

import stripe

from core.models import Plan


stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeApiClient:
    def __init__(self):
        self.domain_url = settings.BASE_URL
        self.logger = logging.getLogger(__name__)

    def get_product(self, product_name):
        products = stripe.Product.list()
        products = products["data"]
        for product in products:
            if product["name"] == product_name and product["active"] == True:
                return product
        return None

    def upload_image(self, image_file_path, purpose="business_logo"):
        with open(image_file_path, "rb") as file:
            image_response = stripe.File.create(purpose=purpose, file=file)
        return image_response

    def create_product(self, product_name, images=None):
        product_response = stripe.Product.create(name=product_name, images=images)
        return product_response

    def get_pricing(self, price_value, currency_value, product_id):
        prices = stripe.Price.list()
        prices = prices["data"]

        for price in prices:
            unit_amount = price["unit_amount"]
            currency = price["currency"]
            product = price["product"]
            if (
                unit_amount == price_value
                and currency == currency_value
                and product == product_id
            ):
                return price
        return None

    def create_pricing(self, price_value, currency_value, interval, product_id):
        recurring_data = {"interval": "month"}
        if interval == Plan.BillingCycle.QUARTERLY:
            recurring_data = {"interval": "month", "interval_count": 3}
        elif interval == Plan.BillingCycle.YEARLY:
            recurring_data = {"interval": "year"}
        price = stripe.Price.create(
            currency=currency_value,
            unit_amount=price_value,
            recurring=recurring_data,
            product=product_id,
        )
        return price

    def create_checkout_session(self, price_id, user_id, plan_id):
        checkout_session = stripe.checkout.Session.create(
            success_url=self.domain_url
            + f"payment/success?user={user_id}&plan={plan_id}",
            cancel_url=self.domain_url + "payment/cancelled/",
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
        )
        return checkout_session
