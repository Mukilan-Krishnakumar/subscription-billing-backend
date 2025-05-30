from django.urls import path

from rest_framework.routers import DefaultRouter

from core import views


router = DefaultRouter()

router.register(r"users", views.UserViewSet, basename="user")
router.register(r"plans", views.PlanViewSet, basename="plan")
router.register(r"subscriptions", views.SubscriptionViewSet, basename="subscription")
router.register(r"invoices", views.InvoiceViewSet, basename="invoice")

urlpatterns = router.urls
