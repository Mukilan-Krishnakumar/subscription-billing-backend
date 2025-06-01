import logging
from zoneinfo import ZoneInfo
from datetime import datetime, timezone

from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from celery import shared_task
from core.constants import STANDARD_DATE_FORMAT, EMAIL_MESSAGES
from core.models import Invoice, Subscription

logger = logging.getLogger(__name__)


@shared_task
def schedule_invoices():
    """
    Scheduled Daily Task which does the following:
    1. Retrieve all active subscriptions
    2. Loop through each subscription
    3. If invoice exists for the subscription - Go to next subscription
    4. Get the Subscription start_at Date
    5. Get the Current Date for Server and User
    6. If the Subscription start_at is greater than or equal to Current Date of User - Create Invoice

    Example 1 (Subscription not yet started, shouldn't create Invoice):
    Subscription Start At Date: 23-May-2025
    User Current Date: 22-May-2025

    Example 2 (Subscription started, should create Invoice):
    Subscription Start At Date: 23-May-2025
    User Current Date: 23-May-2025

    Example 3 (Subscription already started, should create Invoice):
    Subscription Start At Date: 23-May-2025
    User Current Date: 24-May-2025
    """
    logger.info("Running schedule invoice job")
    subscriptions = Subscription.objects.filter(
        status=Subscription.SubscriptionStatus.ACTIVE
    )
    for subscription in subscriptions:
        user = subscription.user
        user_timezone_info = user.timezone_info
        subscription_start_at = subscription.start_date
        user_current_date = datetime.now(tz=ZoneInfo(user_timezone_info)).date()
        if subscription_start_at >= user_current_date:
            invoice_exists = Invoice.objects.filter(subscription=subscription).exists()
            if invoice_exists:
                # If invoice already exists, proceed to the next subscription
                continue

            amount = subscription.plan.price
            currency = subscription.plan.currency
            issue_date = subscription.start_date
            due_date = subscription.start_date
            Invoice.objects.create(
                subscription=subscription,
                amount=amount,
                currency=currency,
                issue_date=issue_date,
                due_date=due_date,
            )
            logger.info(
                "Created invoice object for the user: %s", subscription.user.first_name
            )


@shared_task
def mark_unpaid_invoices():
    """
    Scheduled Daily Task which does the following:
    1. Get list of pending Invoices
    2. Loop through invoices
    3. Retrieve the due_date of the Invoice
    2. Get the current_date of User
    3. If the user_current_date is greater than due_date, mark the invoice as Unpaid
    """
    logger.info("Running marking unpaid invoices job")
    invoices = Invoice.objects.filter(status=Invoice.InvoiceStatus.PENDING)
    for invoice in invoices:
        user = invoice.subscription.user
        user_timezone_info = user.timezone_info
        user_current_date = datetime.now(tz=ZoneInfo(user_timezone_info)).date()
        invoice_due_date = invoice.due_date
        if user_current_date > invoice_due_date:
            invoice.status = Invoice.InvoiceStatus.OVERDUE
            invoice.save(update_fields=["status"])
            logger.info(
                "Marked invoice object as overdue for user: %s", user.first_name
            )


@shared_task
def send_remainder_emails():
    """
    Scheduled Daily Task which sends remainder emails to Pending and Overdue Invoices
    """
    logger.info("Sending remainder emails")
    invoices = Invoice.objects.filter(~Q(status=Invoice.InvoiceStatus.PAID))
    utc_current_time = datetime.now(timezone.utc)
    for invoice in invoices:
        user = invoice.subscription.user
        user_email = user.email
        user_timezone_info = user.timezone_info
        user_current_date = utc_current_time.astimezone(
            ZoneInfo(user_timezone_info)
        ).date()

        user_name = f"{user.first_name} {user.last_name}"
        invoice_id = invoice.id
        user_due_date = invoice.due_date.strftime(STANDARD_DATE_FORMAT)
        amount = invoice.amount
        currency = invoice.currency
        if invoice.status == Invoice.InvoiceStatus.OVERDUE:
            overdue_date = (user_current_date - invoice.due_date).days()
            formatted_message = EMAIL_MESSAGES[invoice.status].format(
                user_name=user_name,
                invoice_id=invoice_id,
                due_date=user_due_date,
                amount=amount,
                currency=currency,
                overdue_date=overdue_date,
            )
            email_subject = "Invoice Overdue"
        else:
            formatted_message = EMAIL_MESSAGES[invoice.status].format(
                user_name=user_name,
                invoice_id=invoice_id,
                due_date=user_due_date,
                amount=amount,
                currency=currency,
            )
            email_subject = "Invoice Pending Payment"
        send_mail(
            subject=email_subject,
            message=formatted_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user_email],
            fail_silently=False,
        )
    logger.info("Successfully sent remainder emails")


@shared_task
def mark_expired_subscriptions():
    """
    Scheduled Daily Task which marks subscriptions as expired.
    """
    logger.info("Marking expired subscriptions")
    subscriptions = Subscription.objects.filter(
        status=Subscription.SubscriptionStatus.ACTIVE
    )
    utc_current_time = datetime.now(timezone.utc)
    for subscription in subscriptions:
        user = subscription.user
        user_timezone_info = user.timezone_info
        user_current_date = utc_current_time.astimezone(
            ZoneInfo(user_timezone_info)
        ).date()
        subscription_end_date = subscription.end_date
        if subscription_end_date < user_current_date:
            subscription.status = Subscription.SubscriptionStatus.EXPIRED
            subscription.save(update_fields=["status"])
            logger.info("Marked an expired subscription")
