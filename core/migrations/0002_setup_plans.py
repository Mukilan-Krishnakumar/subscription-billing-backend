from django.db import migrations
from core.models import Plan
from core.constants import SETUP_PLANS_DATA


def setup_predefined_plans(apps, schema_editor):
    for plan_data in SETUP_PLANS_DATA:
        Plan.objects.get_or_create(
            name=plan_data["name"],
            price=plan_data["price"],
            billing_cycle=plan_data["billing_cycle"],
        )


class Migration(migrations.Migration):

    dependencies = [("core", "0001_initial")]

    operations = [migrations.RunPython(setup_predefined_plans)]
