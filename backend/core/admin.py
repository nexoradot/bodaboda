from django.contrib import admin
from .models import OwnerProfile, RiderProfile, Motorcycle, RiderAssignment, PaymentPlan, Payment, ArrearsPeriod, Notification, AuditLog
admin.site.register([OwnerProfile, RiderProfile, Motorcycle, RiderAssignment, PaymentPlan, Payment, ArrearsPeriod, Notification, AuditLog])
