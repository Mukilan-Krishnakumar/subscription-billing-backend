from django.db import models


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

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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
    integration_info = models.JSONField(default=dict)

    def __str__(self):
        return self.name


class Subscription(BaseModel):
    class SubscriptionStatus(models.TextChoices):
        ACTIVE = "active"
        CANCELLED = "cancelled"
        EXPIRED = "expired"

    user = models.ForeignKey(
        User, related_name="subscription", on_delete=models.CASCADE
    )
    plan = models.ForeignKey(
        Plan, related_name="subscription", on_delete=models.CASCADE
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.TextField(
        choices=SubscriptionStatus.choices, default=SubscriptionStatus.ACTIVE
    )

    def __str__(self):
        return f"{self.user}-{self.plan}-{self.status}"


class Invoice(BaseModel):
    class InvoiceStatus(models.TextChoices):
        PENDING = "pending"
        PAID = "paid"
        OVERDUE = "overdue"

    subscription = models.OneToOneField(
        Subscription, related_name="invoice", on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField()
    currency = models.TextField(default="usd")
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.TextField(
        choices=InvoiceStatus.choices, default=InvoiceStatus.PENDING
    )

    def __str__(self):
        return f"{self.subscription}-{self.status}"
