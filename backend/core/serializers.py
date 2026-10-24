from rest_framework import serializers
from .models import OwnerProfile, RiderProfile, Motorcycle, RiderAssignment, PaymentPlan, Payment, ArrearsPeriod, Notification, AuditLog
class OwnerProfileSerializer(serializers.ModelSerializer):
    class Meta: model = OwnerProfile; fields = "__all__"
class RiderProfileSerializer(serializers.ModelSerializer):
    class Meta: model = RiderProfile; fields = "__all__"
class MotorcycleSerializer(serializers.ModelSerializer):
    class Meta: model = Motorcycle; fields = "__all__"
class RiderAssignmentSerializer(serializers.ModelSerializer):
    class Meta: model = RiderAssignment; fields = "__all__"
class PaymentPlanSerializer(serializers.ModelSerializer):
    class Meta: model = PaymentPlan; fields = "__all__"
class PaymentSerializer(serializers.ModelSerializer):
    class Meta: model = Payment; fields = "__all__"
    def validate(self, attrs):
        if attrs.get("status", Payment.Status.PENDING) == Payment.Status.SUCCESS:
            raise serializers.ValidationError("Successful payment status can only be set by a verified payment callback.")
        return attrs
class ArrearsPeriodSerializer(serializers.ModelSerializer):
    class Meta: model = ArrearsPeriod; fields = "__all__"
class NotificationSerializer(serializers.ModelSerializer):
    class Meta: model = Notification; fields = "__all__"
class AuditLogSerializer(serializers.ModelSerializer):
    class Meta: model = AuditLog; fields = "__all__"
