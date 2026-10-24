from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models import Motorcycle, RiderAssignment, PaymentPlan, Payment, ArrearsPeriod, Notification
from .serializers import MotorcycleSerializer, RiderAssignmentSerializer, PaymentPlanSerializer, PaymentSerializer, ArrearsPeriodSerializer, NotificationSerializer
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health(request):
    return Response({"status":"ok","service":"BodaPay API scaffold","payments":"demo/not configured"})
class SafeModelViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
class MotorcycleViewSet(SafeModelViewSet):
    queryset = Motorcycle.objects.select_related("owner").all()
    serializer_class = MotorcycleSerializer
class RiderAssignmentViewSet(SafeModelViewSet):
    queryset = RiderAssignment.objects.select_related("motorcycle","rider").all()
    serializer_class = RiderAssignmentSerializer
class PaymentPlanViewSet(SafeModelViewSet):
    queryset = PaymentPlan.objects.select_related("motorcycle").all()
    serializer_class = PaymentPlanSerializer
class PaymentViewSet(SafeModelViewSet):
    queryset = Payment.objects.select_related("plan","rider").all()
    serializer_class = PaymentSerializer
    http_method_names = ["get","post","head","options"]
    @action(detail=False, methods=["post"], url_path="stk-push")
    def stk_push(self, request):
        return Response({"status":"not_configured","message":"Daraja is not configured. No payment was initiated."}, status=status.HTTP_501_NOT_IMPLEMENTED)
    @action(detail=False, methods=["post"], url_path="mpesa/callback", permission_classes=[permissions.AllowAny], authentication_classes=[])
    def mpesa_callback(self, request):
        return Response({"status":"not_configured","message":"Callback verification is not configured; transaction was not recorded."}, status=status.HTTP_501_NOT_IMPLEMENTED)
class ArrearsPeriodViewSet(SafeModelViewSet):
    queryset = ArrearsPeriod.objects.select_related("plan").all()
    serializer_class = ArrearsPeriodSerializer
class NotificationViewSet(SafeModelViewSet):
    queryset = Notification.objects.select_related("user").all()
    serializer_class = NotificationSerializer
