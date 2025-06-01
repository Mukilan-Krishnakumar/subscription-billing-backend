from zoneinfo import ZoneInfo
from datetime import datetime
from dateutil.relativedelta import relativedelta

from core.models import Plan
from core.constants import SETUP_PLANS_DATA

# datetime's timedelta doesn't support months, hence using relativedelta


def get_current_date(timezone_info):
    return datetime.now(ZoneInfo(timezone_info)).date()


def generate_end_date(billing_cycle, start_date):
    end_date = None
    if billing_cycle == Plan.BillingCycle.MONTHLY:
        end_date = start_date + relativedelta(months=1)
    elif billing_cycle == Plan.BillingCycle.QUARTERLY:
        end_date = start_date + relativedelta(months=3)
    elif billing_cycle == Plan.BillingCycle.YEARLY:
        end_date = start_date + relativedelta(years=1)
    return end_date


def setup_predefined_plans():
    for plan_data in SETUP_PLANS_DATA:
        Plan.objects.get_or_create(
            name=plan_data["name"],
            price=plan_data["price"],
            billing_cycle=plan_data["billing_cycle"],
        )
