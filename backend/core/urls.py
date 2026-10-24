from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MotorcycleViewSet, RiderAssignmentViewSet, PaymentPlanViewSet, PaymentViewSet, ArrearsPeriodViewSet, NotificationViewSet, health
router = DefaultRouter()
router.register("motorcycles", MotorcycleViewSet)
router.register("assignments", RiderAssignmentViewSet)
router.register("payment-plans", PaymentPlanViewSet)
router.register("payments", PaymentViewSet)
router.register("arrears", ArrearsPeriodViewSet)
router.register("notifications", NotificationViewSet)
urlpatterns = [path("health/", health), path("", include(router.urls))]
