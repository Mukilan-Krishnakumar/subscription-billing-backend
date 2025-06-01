import pytest

from core.models import User, Plan, Subscription, Invoice


@pytest.fixture
def user():
    user_data = {
        "first_name": "Mukilan",
        "last_name": "Krishnakumar",
        "email": "mukilankrishnakumar2002@gmail.com",
        "timezone_info": "Asia/Kolkata",
    }
    user = User.objects.create(
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        email=user_data["email"],
        timezone_info=user_data["timezone_info"],
    )
    return user


@pytest.fixture
def plan():
    plan_data = {
        "name": "Basic",
        "price": 20,
        "currency": "usd",
        "billing_cycle": "monthly",
        "integration_info": "{}",
    }
    plan = Plan.objects.create(
        name=plan_data["name"],
        price=plan_data["price"],
        currency=plan_data["currency"],
        billing_cycle=plan_data["billing_cycle"],
        integration_info=plan_data["integration_info"],
    )

    return plan


@pytest.fixture
def pro_plan():
    plan_data = {
        "name": "Pro",
        "price": 50,
        "currency": "usd",
        "billing_cycle": "monthly",
        "integration_info": "{}",
    }
    plan = Plan.objects.create(
        name=plan_data["name"],
        price=plan_data["price"],
        currency=plan_data["currency"],
        billing_cycle=plan_data["billing_cycle"],
        integration_info=plan_data["integration_info"],
    )

    return plan


@pytest.fixture
def active_subscription(user, plan):
    subscription_data = {
        "user": user,
        "plan": plan,
        "start_date": "2025-06-01",
        "end_date": "2025-07-01",
        "status": "active",
    }
    subscription = Subscription.objects.create(
        user=subscription_data["user"],
        plan=subscription_data["plan"],
        start_date=subscription_data["start_date"],
        end_date=subscription_data["end_date"],
        status=subscription_data["status"],
    )
    return subscription


@pytest.fixture
def alternate_active_subscription(user, pro_plan):
    subscription_data = {
        "user": user,
        "plan": pro_plan,
        "start_date": "2025-06-01",
        "end_date": "2025-07-01",
        "status": "active",
    }
    subscription = Subscription.objects.create(
        user=subscription_data["user"],
        plan=subscription_data["plan"],
        start_date=subscription_data["start_date"],
        end_date=subscription_data["end_date"],
        status=subscription_data["status"],
    )
    return subscription


@pytest.fixture
def unmarked_subscription(user, plan):
    subscription_data = {
        "user": user,
        "plan": plan,
        "start_date": "2025-04-01",
        "end_date": "2025-05-01",
        "status": "active",
    }
    subscription = Subscription.objects.create(
        user=subscription_data["user"],
        plan=subscription_data["plan"],
        start_date=subscription_data["start_date"],
        end_date=subscription_data["end_date"],
        status=subscription_data["status"],
    )
    return subscription


@pytest.fixture
def pending_invoice(active_subscription):
    invoice_data = {
        "subscription": active_subscription,
        "amount": 20,
        "currency": "usd",
        "issue_date": "2025-06-01",
        "due_date": "2025-06-01",
        "status": "pending",
    }
    invoice = Invoice.objects.create(
        subscription=invoice_data["subscription"],
        amount=invoice_data["amount"],
        currency=invoice_data["currency"],
        issue_date=invoice_data["issue_date"],
        due_date=invoice_data["due_date"],
        status=invoice_data["status"],
    )

    return invoice
