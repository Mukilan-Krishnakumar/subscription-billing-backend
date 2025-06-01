import pytest

from core.actions.payment_actions import SuccessfullPaymentAction
from core.models import User
from core.tests.fixtures import *


@pytest.mark.django_db
class TestSuccessfullPaymentAction:
    def test_success_payment(self, user, plan):
        user_id = user.id
        plan_id = plan.id
        action = SuccessfullPaymentAction(user_id=user_id, plan_id=plan_id)
        success, result = action.execute()
        assert success

    def test_invalid_user(self, plan):
        user_id = 35
        plan_id = plan.id
        with pytest.raises(User.DoesNotExist):
            SuccessfullPaymentAction(user_id=user_id, plan_id=plan_id)

    def test_invalid_plan(self, user):
        user_id = user.id
        plan_id = 35
        with pytest.raises(Plan.DoesNotExist):
            SuccessfullPaymentAction(user_id=user_id, plan_id=plan_id)

    def test_existing_active_subscription(self, user, plan, active_subscription):
        user_id = user.id
        plan_id = plan.id
        action = SuccessfullPaymentAction(user_id=user_id, plan_id=plan_id)
        success, result = action.execute()
        assert not success
        assert (
            result
            == "Found already active subscriptions, one user cannot have multiple active subscriptions"
        )
