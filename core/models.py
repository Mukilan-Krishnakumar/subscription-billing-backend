from django.db import models


# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    first_name = models.TextField()
    last_name = models.TextField(null=True, blank=True)
    email = models.EmailField(unique=True)
    timezone_info = models.TextField()


class Plan(BaseModel):
    class BillingCycle(models.TextChoices):
        MONTHLY = "monthly"
        YEARLY = "yearly"
        QUARTERLY = "quarterly"

    name = models.TextField()
    price = models.PositiveIntegerField()
    currency = models.TextField(default="usd")
    billing_cycle = models.TextField(
        choices=BillingCycle.choices, default=BillingCycle.YEARLY
    )


class Subscription(BaseModel):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active"
        CANCELLED = "cancelled"
        EXPIRED = "expired"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    next_billing_date = models.DateField(null=True, blank=True)
    status = models.TextField(
        choices=SubscriptionStatus.choices, default=SubscriptionStatus.ACTIVE
    )


class Invoice(BaseModel):
    class InvoiceStatus(models.TextChoices):
        PENDING = "pending"
        PAID = "paid"

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    currency = models.TextField(default="usd")
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.TextField(
        choices=InvoiceStatus.choices, default=InvoiceStatus.PENDING
    )
