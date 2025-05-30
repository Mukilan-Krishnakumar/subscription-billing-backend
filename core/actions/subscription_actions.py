from core.models import User, Subscription
from core.helpers import generate_start_date, generate_end_date


class CreateSubscriptionAction:
    def __init__(self, serializer):

        self.serializer = serializer
        self.data = serializer.validated_data

        self.user = self.data["user"]
        self.plan = self.data["plan"]

    def check_existing_subscriptions(self):
        # TODO: Add date check also (based on end_date)
        subscriptions = Subscription.objects.filter(
            user=self.user,
            status=Subscription.SubscriptionStatus.ACTIVE,
        )
        if subscriptions:
            return True
        return False

    def get_start_date(self):
        timezone_info = self.user.timezone_info
        start_date = generate_start_date(timezone_info=timezone_info)
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
            return True, {"message": "Successfully created subscription"}

        return False, {"error": "Subscription already exists"}


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
        # TODO: Make this better
        try:
            subscription = Subscription.objects.get(
                user=user, status=Subscription.SubscriptionStatus.ACTIVE
            )
            return subscription
        except Subscription.DoesNotExist:
            return None
        except Subscription.MultipleObjectsReturned:
            return None

    def execute(self):
        user = self.get_user()
        if not user:
            return {"error": "User doesn't exist with the given ID"}
        subscription = self.get_active_subscription(user=user)
        if not subscription:
            return {"error": "There is no active subscription"}
        subscription.status = Subscription.SubscriptionStatus.CANCELLED
        subscription.save(update_fields=["status"])
        return {"success": "True"}
