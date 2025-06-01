from core.models import User, Subscription
from core.helpers import generate_end_date, get_current_date


class CreateSubscriptionAction:
    def __init__(self, serializer):
        self.serializer = serializer
        self.data = serializer.validated_data

        self.user = self.data["user"]
        self.plan = self.data["plan"]

    def check_existing_subscriptions(self):
        """
        Assumes that the periodic task which marks subscription as Cancelled
        is working as intended.
        """
        subscriptions = Subscription.objects.filter(
            user=self.user,
            status=Subscription.SubscriptionStatus.ACTIVE,
        )
        if subscriptions:
            return True
        return False

    def get_start_date(self):
        timezone_info = self.user.timezone_info
        start_date = get_current_date(timezone_info=timezone_info)
        return start_date

    def get_end_date(self, start_date):
        plan = self.plan
        billing_cycle = plan.billing_cycle
        end_date = generate_end_date(billing_cycle=billing_cycle, start_date=start_date)
        return end_date

    def execute(self):
        existing_subscription = self.check_existing_subscriptions()
        if not existing_subscription:
            subscription = self.serializer.save()
            start_date = self.get_start_date()
            end_date = self.get_end_date(start_date=start_date)
            subscription.start_date = start_date
            subscription.end_date = end_date
            subscription.save(update_fields=["start_date", "end_date"])
            return True, "Successfully created subscription"

        return False, "Subscription already exists"


class UnsubscribeAction:
    def __init__(self, user_id):
        self.user_id = user_id

    def get_user(self):
        try:
            user = User.objects.get(id=self.user_id)
            return user
        except User.DoesNotExist:
            return None

    def get_active_subscription(self, user):
        try:
            subscription = Subscription.objects.get(
                user=user, status=Subscription.SubscriptionStatus.ACTIVE
            )
            return subscription
        except Subscription.DoesNotExist:
            return None

    def execute(self):
        user = self.get_user()
        if not user:
            return False, "User with the given user_id doesn't exist"
        user_name = user.first_name + user.last_name
        try:
            subscription = self.get_active_subscription(user=user)
        except Subscription.MultipleObjectsReturned:
            return False, "Multiple active subscriptions exist at the same time"
        if not subscription:
            return False, f"No active subscription found for {user_name}"
        subscription.status = Subscription.SubscriptionStatus.CANCELLED
        subscription.save(update_fields=["status"])
        return (
            True,
            f"{user_name} Unsubscribed from {subscription.plan.name}",
        )
