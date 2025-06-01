from django.core.management.base import BaseCommand

from core.helpers import setup_predefined_plans
from core.actions.setup_actions import SetupStripeEntitiesAction


class Command(BaseCommand):
    help = "Sets up basic plans along with their associated Stripe entities"

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write(self.style.HTTP_INFO("Setting up predefined data plans"))
            setup_predefined_plans()
            self.stdout.write(self.style.HTTP_INFO("Setting up stripe entities"))
            SetupStripeEntitiesAction().execute()
            self.stdout.write(
                self.style.SUCCESS(
                    "Successfully set up basic plans along with their associated Stripe entities"
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to setup basic plans along with stripe entities due to following exception:  {str(e)}"
                )
            )
