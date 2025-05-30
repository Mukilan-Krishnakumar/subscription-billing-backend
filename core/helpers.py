from zoneinfo import ZoneInfo
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from core.models import Plan

# timedelta doesn't have months


def generate_start_date(timezone_info):
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
