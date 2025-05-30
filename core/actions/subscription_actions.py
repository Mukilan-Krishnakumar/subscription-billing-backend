from core.models import User, Subscription


class CreateSubscriptionAction:
    def __init__(self, serializer):

        self.serializer = serializer
        self.data = serializer.validated_data

        self.user = self.data["user"]
        self.plan = self.data["plan"]
        self.start_date = self.data["start_date"]
        self.end_date = self.data["end_date"]
        self.next_billing_date = self.data.get("next_billing_date")

    def check_existing_subscriptions(self):
        # TODO: Add date check also (based on end_date)
        subscriptions = Subscription.objects.filter(
            user=self.user,
            plan=self.plan,
            status=Subscription.SubscriptionStatus.ACTIVE,
        )
        if subscriptions:
            return True
        return False

    def execute(self):
        existing_subscription = self.check_existing_subscriptions()
        if not existing_subscription:
            self.serializer.save()
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
