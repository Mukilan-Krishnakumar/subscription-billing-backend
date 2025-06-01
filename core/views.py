import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


from core import models
from core import serializers as core_serializers
from core.actions import subscription_actions, payment_actions
from integrations.stripe.api_client import StripeApiClient

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = core_serializers.UserSerializer
    queryset = models.User.objects.all()


class PlanViewSet(viewsets.ModelViewSet):
    serializer_class = core_serializers.PlanSerializer
    queryset = models.Plan.objects.all()


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = core_serializers.InvoiceSerializer
    queryset = models.Invoice.objects.all()


class SubscriptionViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = models.Subscription.objects.all()
        serializer = core_serializers.SubscriptionListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["post"], detail=False)
    def subscribe(self, request):
        body = request.body
        if not body:
            return Response(
                {"error": "request body cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = json.loads(request.body)
        serializer = core_serializers.SubscriptionSerializer(data=data)
        if serializer.is_valid():
            success, message = subscription_actions.CreateSubscriptionAction(
                serializer=serializer
            ).execute()
        else:
            return Response(serializer._errors)

        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": message}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

    @action(methods=["post"], detail=False)
    def unsubscribe(self, request):
        body = request.body
        if not body:
            return Response(
                {"error": "request body cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = json.loads(request.body)
        user_id = data.get("user")
        if not user_id:
            return Response(
                {"error": "user_id field cannot be empty"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success, message = subscription_actions.UnsubscribeAction(
            user_id=user_id
        ).execute()
        if not success:
            return Response(
                {"error": message}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return Response({"message": message}, status=status.HTTP_200_OK)


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


@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        body = json.loads(request.body)
        plan_id = body.get("plan_id")
        try:
            plan = models.Plan.objects.get(id=plan_id)
        except models.Plan.DoesNotExist:
            return JsonResponse(
                {"error": "Given plan_id is not a valid plan_id"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except Exception as e:
            return JsonResponse(
                {"error": str(e)},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        price_id = plan.integration_info.get("stripe", {}).get("price_id")
        # This should be the actual User ID - We don't have auth yet, so choosing the first user
        user_id = models.User.objects.first().id
        try:
            checkout_session = StripeApiClient().create_checkout_session(
                price_id=price_id, user_id=user_id, plan_id=plan.id
            )
            return JsonResponse(
                {"sessionId": checkout_session["id"]}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return JsonResponse(
                {"error": str(e)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )


class PaymentViewSet(viewsets.ViewSet):
    @action(methods=["get"], detail=False)
    def status(self, request):
        queryset = models.Invoice.objects.all()
        serializer = core_serializers.PaymentSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=["get"], url_path="success", detail=False)
    def success(self, request):
        params = request.GET
        user_id = int(params.get("user"))
        plan_id = int(params.get("plan"))
        try:
            action = payment_actions.SuccessfullPaymentAction(
                user_id=user_id, plan_id=plan_id
            )
        except models.User.DoesNotExist:
            return JsonResponse(
                {"user": "Given user_id is not a valid user_id"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except models.Plan.DoesNotExist:
            return JsonResponse(
                {"plan": "Given plan_id is not a valid plan_id"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        success, message = action.execute()
        if not success:
            return JsonResponse(
                {"message": message}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        return JsonResponse({"message": message}, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False)
    def cancelled(self, request):
        return JsonResponse(
            {"message": "The transaction was cancelled"}, status=status.HTTP_200_OK
        )
