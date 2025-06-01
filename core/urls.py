from django.urls import path

from rest_framework.routers import DefaultRouter

from core import views


router = DefaultRouter()

router.register(r"api/users", views.UserViewSet, basename="user")
router.register(r"api/plans", views.PlanViewSet, basename="plan")
router.register(
    r"api/subscriptions", views.SubscriptionViewSet, basename="subscription"
)
router.register(r"api/invoices", views.InvoiceViewSet, basename="invoice")
router.register(r"purchase", views.PurchaseViewSet, basename="purchase")
router.register(r"payment", views.PaymentViewSet, basename="payment")

urlpatterns = [
    path("checkout-session/", views.create_checkout_session),
] + router.urls
