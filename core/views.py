import json
import logging

import stripe
from django.conf import settings
from django.views.generic.base import TemplateView
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse

from core import models
from core import serializers as core_serializers
from core.actions import subscription_actions

from core.actions.setup_actions import SetupStripeEntitiesAction
from integrations.stripe.api_client import StripeApiClient

logger = logging.getLogger(__name__)


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = core_serializers.UserSerializer
    queryset = models.User.objects.all()


class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = core_serializers.PlanSerializer
    queryset = models.Plan.objects.all()


class SubscriptionViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = models.Subscription.objects.all()
        serializer = core_serializers.SubscriptionListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["post"], detail=False)
    def subscribe(self, request):
        body = request.body
        if not body:
            return Response({"error": "body cannot be empty"})
        data = json.loads(request.body)
        serializer = core_serializers.SubscriptionSerializer(data=data)
        if serializer.is_valid():
            response = subscription_actions.CreateSubscriptionAction(
                serializer=serializer
            ).execute()
        else:
            return Response(serializer._errors)
        return Response(response)

    @action(methods=["post"], detail=False)
    def unsubscribe(self, request):
        # TODO: Create an unsubscribe serializer and get the data throught that
        body = request.body
        if not body:
            return Response({"error": "body cannot be empty"})
        data = json.loads(request.body)
        user_id = data.get("user")
        if not user_id:
            return Response({"error": "user_id needed"})
        response = subscription_actions.UnsubscribeAction(user_id=user_id).execute()
        return Response(response)


class InvoiceViewSet(viewsets.ViewSet):

    # TODO: Revisit Payments view once Stripe Integration is done

    def list(self, request):
        queryset = models.Invoice.objects.all()
        serializer = core_serializers.InvoiceSerializer(queryset, many=True)
        return Response(serializer.data)


class PurchaseViewSet(viewsets.ViewSet):
    @action(methods=["get"], detail=False)
    def pricing(self, request):
        queryset = models.Plan.objects.all()
        serializer = core_serializers.PlanSerializer(queryset, many=True)
        context = {"plans": serializer.data}
        return render(request, "plan_page.html", context=context)

    @action(methods=["get"], url_path="stripe-config", detail=False)
    def stripe_config(self, request):
        stripe_config = {"publicKey": settings.STRIPE_PUBLISHABLE_KEY}
        return Response(stripe_config, status=200)

    @action(methods=["post"], url_path="checkout-session", detail=False)
    def checkout_session(self, request):
        body = json.loads(request.body)
        plan_id = body.get("plan_id")
        domain_url = "http://localhost:8000/"
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # TODO: Handle Exception
        plan = models.Plan.objects.get(id=plan_id)
        price_id = plan.integration_info.get("stripe", {}).get("price_id")
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "cancelled/",
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{"price": price_id, "quantity": 1}],
            )
            return Response({"sessionId": checkout_session["id"]})
        except Exception as e:
            return JsonResponse({"error": str(e)})


@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        body = json.loads(request.body)
        plan_id = body.get("plan_id")
        # TODO: Handle Exception
        plan = models.Plan.objects.get(id=plan_id)
        price_id = plan.integration_info.get("stripe", {}).get("price_id")
        try:
            checkout_session = StripeApiClient().create_checkout_session(
                price_id=price_id
            )
            return JsonResponse({"sessionId": checkout_session["id"]})
        except Exception as e:
            return JsonResponse({"error": str(e)})


# TODO: Port this to a management command
def check_stripe_action(request):
    SetupStripeEntitiesAction().execute()
    return JsonResponse({"status": "ok"})
