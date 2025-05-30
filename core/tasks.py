import logging
from zoneinfo import ZoneInfo
from datetime import datetime, timezone, timedelta

from celery import shared_task
from core.models import Invoice, Subscription

logger = logging.getLogger(__name__)


@shared_task
def schedule_invoice():
    """
    Runs every day
    Convert to datetime and compare

    All datetime operations done in UTC
    """
    logger.info("Running schedule invoice job")
    subscriptions = Subscription.objects.filter(
        status=Subscription.SubscriptionStatus.ACTIVE
    )
    utc_current_time = datetime.now(timezone.utc)
    for subscription in subscriptions:
        user = subscription.user
        user_timezone_info = user.timezone_info
        server_current_date = utc_current_time.astimezone(
            ZoneInfo(user_timezone_info)
        ).date()
        user_current_date = datetime.now(tz=ZoneInfo(user_timezone_info)).date()
        if user_current_date <= server_current_date:
            # Only create invoices for the one day window
            try:
                invoice = Invoice.objects.get(
                    subscription=subscription,
                )
                # Depending on invoice status - some action
                continue
            except Invoice.DoesNotExist:
                pass

            user_timezone_info = subscription.user.timezone_info

            issue_date = subscription.start_date
            due_date = subscription.start_date
            # TODO: Add user currency conversion
            amount = subscription.plan.price
            currency = subscription.plan.currency
            invoice = Invoice.objects.create(
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
    logger.info("Running marking unpaid invoices job")
    invoices = Invoice.objects.filter(status=Invoice.InvoiceStatus.PENDING)
    for invoice in invoices:
        user = invoice.subscription.user
        user_timezone_info = user.timezone_info
        user_current_date = datetime.now(tz=ZoneInfo(user_timezone_info)).date()
        user_due_date = invoice.due_date
        if user_current_date > user_due_date:
            invoice.status = Invoice.InvoiceStatus.OVERDUE
            invoice.save(update_fields=["status"])
            logger.info(
                "Marked invoice object as overdue for user: %s", user.first_name
            )
