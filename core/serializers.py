from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from rest_framework import serializers

from core import models
from core import constants


class UserSerializer(serializers.ModelSerializer):

    def validate_timezone_info(self, value):
        try:
            ZoneInfo(value)
            return value
        except ZoneInfoNotFoundError:
            raise serializers.ValidationError("Entered timezone is not of IANA format")

    class Meta:
        model = models.User
        fields = ["first_name", "last_name", "email", "timezone_info"]


class PlanSerializer(serializers.ModelSerializer):
    def validate_currency(self, value):
        value = value.lower()
        if value not in constants.SUPPORTED_CURRENCIES:
            raise serializers.ValidationError(
                "Entered currency is not on our supported currencies"
            )
        return value

    class Meta:
        model = models.Plan
        fields = ["name", "price", "currency", "billing_cycle"]


class SubscriptionListSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    plan = PlanSerializer()

    def validate_user(self, value):
        try:
            user = models.User.objects.get(id=value)
        except models.User.DoesNotExist:
            raise serializers.ValidationError("User with the id does not exist")
        return user

    class Meta:
        model = models.Subscription
        fields = [
            "user",
            "plan",
            "start_date",
            "end_date",
            "next_billing_date",
            "status",
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subscription
        fields = [
            "user",
            "plan",
            "start_date",
            "end_date",
            "next_billing_date",
            "status",
        ]


class InvoiceSerializer(serializers.ModelSerializer):
    subscription = SubscriptionListSerializer()

    class Meta:
        model = models.Invoice
        fields = [
            "subscription",
            "amount",
            "currency",
            "issue_date",
            "due_date",
            "status",
        ]
