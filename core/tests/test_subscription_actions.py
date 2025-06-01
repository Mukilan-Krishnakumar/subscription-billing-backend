import pytest
from unittest.mock import Mock

from core.actions.subscription_actions import (
    CreateSubscriptionAction,
    UnsubscribeAction,
)
from core.tests.fixtures import *


@pytest.mark.django_db
class TestCreateSubscriptionAction:
    def test_create_subscription_action(self, user, plan):
        mock_serializer = Mock()
        mock_serializer.validated_data = {"user": user, "plan": plan}
        action = CreateSubscriptionAction(serializer=mock_serializer)
        success, result = action.execute()
        assert success
        assert result == "Successfully created subscription"

    def test_existing_active_subscription(self, user, plan, active_subscription):
        mock_serializer = Mock()
        mock_serializer.validated_data = {"user": user, "plan": plan}
        action = CreateSubscriptionAction(serializer=mock_serializer)
        success, result = action.execute()
        assert not success
        assert result == "Subscription already exists"


@pytest.mark.django_db
class TestUnsubscribeAction:
    def test_unsubscribe_action(self, user, active_subscription):
        user_id = user.id
        user_name = f"{user.first_name} {user.last_name}"
        action = UnsubscribeAction(user_id=user_id)
        success, result = action.execute()
        assert success
        assert (
            result == f"{user_name} Unsubscribed from {active_subscription.plan.name}"
        )

    def test_unexisting_user(self):
        user_id = 35
        action = UnsubscribeAction(user_id=user_id)
        success, result = action.execute()
        assert not success
        assert result == "User with the given user_id doesn't exist"

    def test_multiple_active_subscriptions(
        self, user, active_subscription, alternate_active_subscription
    ):
        user_id = user.id
        action = UnsubscribeAction(user_id=user_id)
        success, result = action.execute()
        assert not success
        assert result == "Multiple active subscriptions exist at the same time"

    def test_no_active_subscription(self, user):
        user_id = user.id
        user_name = f"{user.first_name} {user.last_name}"
        action = UnsubscribeAction(user_id=user_id)
        success, result = action.execute()
        assert not success
        assert result == f"No active subscription found for {user_name}"
