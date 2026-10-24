from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
class Timestamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: abstract = True
class OwnerProfile(Timestamped):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owner_profile")
    mpesa_number = models.CharField(max_length=20, blank=True)
    def __str__(self): return f"Owner: {self.user.get_username()}"
class RiderProfile(Timestamped):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rider_profile")
    id_number = models.CharField(max_length=30, blank=True)
    license_number = models.CharField(max_length=40, blank=True)
    mpesa_number = models.CharField(max_length=20, blank=True)
    def __str__(self): return f"Rider: {self.user.get_username()}"
class Motorcycle(Timestamped):
    class Status(models.TextChoices): ACTIVE="active", "Active"; INACTIVE="inactive", "Inactive"; MAINTENANCE="maintenance", "Maintenance"
    registration_number = models.CharField(max_length=20, unique=True)
    owner = models.ForeignKey(OwnerProfile, on_delete=models.PROTECT, related_name="motorcycles")
    make_model = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    def __str__(self): return self.registration_number
class RiderAssignment(Timestamped):
    motorcycle = models.ForeignKey(Motorcycle, on_delete=models.PROTECT, related_name="assignments")
    rider = models.ForeignKey(RiderProfile, on_delete=models.PROTECT, related_name="assignments")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    class Meta: ordering = ["-start_date"]
class PaymentPlan(Timestamped):
    class Status(models.TextChoices): ACTIVE="active", "Active"; PAUSED="paused", "Paused"; COMPLETED="completed", "Completed"
    motorcycle = models.ForeignKey(Motorcycle, on_delete=models.PROTECT, related_name="payment_plans")
    daily_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    penalty_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    penalty_grace_days = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)
class Payment(Timestamped):
    class Status(models.TextChoices): PENDING="pending", "Pending"; SUCCESS="success", "Success"; FAILED="failed", "Failed"; REVERSED="reversed", "Reversed"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(PaymentPlan, on_delete=models.PROTECT, related_name="payments")
    rider = models.ForeignKey(RiderProfile, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    channel = models.CharField(max_length=20, default="mpesa")
    transaction_code = models.CharField(max_length=40, null=True, blank=True, unique=True)
    checkout_request_id = models.CharField(max_length=120, blank=True, db_index=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    receipt_number = models.CharField(max_length=40, blank=True, unique=True)
    note = models.TextField(blank=True)
class ArrearsPeriod(Timestamped):
    plan = models.ForeignKey(PaymentPlan, on_delete=models.PROTECT, related_name="arrears_periods")
    period_start = models.DateField()
    period_end = models.DateField()
    required_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    qualifying_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    penalty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    assessed_at = models.DateTimeField(null=True, blank=True)
    class Meta: constraints = [models.UniqueConstraint(fields=["plan","period_start","period_end"], name="uniq_plan_arrears_period")]
class Notification(Timestamped):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="boda_notifications")
    type = models.CharField(max_length=40)
    message = models.TextField()
    read_at = models.DateTimeField(null=True, blank=True)
class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=60)
    entity = models.CharField(max_length=60)
    entity_id = models.CharField(max_length=120)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    remote_ip = models.GenericIPAddressField(null=True, blank=True)
    class Meta: ordering = ["-created_at"]


class DailyObligation(Timestamped):
    plan = models.ForeignKey(PaymentPlan, on_delete=models.PROTECT, related_name="daily_obligations")
    rider = models.ForeignKey(RiderProfile, on_delete=models.PROTECT, related_name="daily_obligations")
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    status = models.CharField(max_length=12, choices=[("due", "Due"), ("paused", "Paused"), ("void", "Voided")], default="due")
    terms_snapshot = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["due_date", "id"]
        constraints = [models.UniqueConstraint(fields=["plan", "due_date"], name="uniq_daily_obligation_plan_date")]


class LedgerEntry(Timestamped):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    obligation = models.ForeignKey(DailyObligation, on_delete=models.PROTECT, null=True, blank=True, related_name="ledger_entries")
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, null=True, blank=True, related_name="ledger_entries")
    entry_type = models.CharField(max_length=12, choices=[("payment", "Payment"), ("reversal", "Reversal"), ("adjustment", "Adjustment")])
    category = models.CharField(max_length=12, choices=[("principal", "Principal"), ("penalty", "Penalty")], default="principal")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    idempotency_key = models.CharField(max_length=120, unique=True)
    description = models.CharField(max_length=240, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reverses = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True, related_name="reversal_entries")

    class Meta:
        ordering = ["created_at", "id"]
