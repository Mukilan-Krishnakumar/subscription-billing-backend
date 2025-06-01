import logging

from core.models import User, Plan, Subscription, Invoice
from core.helpers import generate_end_date, get_current_date


class SuccessfullPaymentAction:
    def __init__(self, user_id, plan_id):
        self.user = User.objects.get(id=user_id)
        self.plan = Plan.objects.get(id=plan_id)
        self.logger = logging.getLogger(__name__)

    def create_active_subscription(self):
        self.logger.info("Creating active subscription")
        start_date = get_current_date(timezone_info=self.user.timezone_info)
        end_date = generate_end_date(
            billing_cycle=self.plan.billing_cycle, start_date=start_date
        )
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status=Subscription.SubscriptionStatus.ACTIVE,
            start_date=start_date,
            end_date=end_date,
        )
        return subscription

    def get_active_subscriptions(self):
        subscriptions = Subscription.objects.filter(
            user=self.user, status=Subscription.SubscriptionStatus.ACTIVE
        )
        return subscriptions

    def create_paid_invoice(self, subscription):
        self.logger.info("Creating paid invoice")
        due_date = get_current_date(timezone_info=self.user.timezone_info)
        invoice = Invoice.objects.create(
            subscription=subscription,
            amount=self.plan.price,
            currency=self.plan.currency,
            issue_date=subscription.start_date,
            due_date=due_date,
            status=Invoice.InvoiceStatus.PAID,
        )
        return invoice

    def get_pending_invoice(self, subscription):
        invoice = Invoice.objects.get(subscription=subscription)
        return invoice

    def execute(self):
        active_subscriptions = self.get_active_subscriptions()
        if active_subscriptions:
            return (
                False,
                "Found already active subscriptions, one user cannot have multiple active subscriptions",
            )

        subscription = self.create_active_subscription()
        self.create_paid_invoice(subscription=subscription)
        return True, "Succesfully purchased subscription"
