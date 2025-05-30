import json
from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from core import models
from core import serializers as core_serializers
from core.actions import subscription_actions


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
