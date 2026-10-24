from decimal import Decimal

from django.db import models, transaction
from django.db.models import Q, Sum
from django.utils import timezone

from .models import DailyObligation, LedgerEntry, Payment, PaymentPlan, RiderAssignment


@transaction.atomic
def generate_daily_obligations(day=None, plan_id=None):
    """Create today's obligations idempotently for active plans with an active rider."""
    day = day or timezone.localdate()
    plans = PaymentPlan.objects.filter(
        status=PaymentPlan.Status.ACTIVE,
        start_date__lte=day,
    ).filter(Q(end_date__isnull=True) | Q(end_date__gte=day))
    if plan_id is not None:
        plans = plans.filter(pk=plan_id)

    created = 0
    skipped = []
    for plan in plans.select_related("motorcycle").order_by("pk"):
        assignment = RiderAssignment.objects.filter(
            motorcycle=plan.motorcycle,
            start_date__lte=day,
        ).filter(Q(end_date__isnull=True) | Q(end_date__gte=day)).order_by("-start_date", "-pk").first()
        if assignment is None:
            skipped.append({"plan_id": plan.pk, "reason": "no active rider assignment"})
            continue
        _, was_created = DailyObligation.objects.get_or_create(
            plan=plan,
            due_date=day,
            defaults={
                "rider": assignment.rider,
                "amount_due": plan.daily_amount,
                "terms_snapshot": {
                    "daily_amount": str(plan.daily_amount),
                    "penalty_percent": str(plan.penalty_percent),
                    "penalty_grace_days": plan.penalty_grace_days,
                },
            },
        )
        created += int(was_created)
    return {"date": day.isoformat(), "created": created, "skipped": skipped}


@transaction.atomic
def record_verified_payment(payment, provider_transaction_code, confirmed_at=None):
    """Record a provider-confirmed payment; call only after authenticating provider evidence."""
    code = (provider_transaction_code or "").strip()
    if not code:
        raise ValueError("A verified provider transaction code is required.")

    locked = Payment.objects.select_for_update().get(pk=payment.pk)
    if locked.status == Payment.Status.SUCCESS:
        if locked.transaction_code == code:
            return locked, False
        raise ValueError("Payment is already confirmed under a different transaction code.")
    if locked.status != Payment.Status.PENDING:
        raise ValueError("Only pending payments can be confirmed.")

    locked.status = Payment.Status.SUCCESS
    locked.transaction_code = code
    locked.paid_at = confirmed_at or timezone.now()
    locked.save(update_fields=["status", "transaction_code", "paid_at", "updated_at"])

    LedgerEntry.objects.get_or_create(
        idempotency_key=f"provider-payment:{code}",
        defaults={
            "payment": locked,
            "entry_type": "payment",
            "category": "principal",
            "amount": locked.amount,
            "description": "Verified provider payment",
        },
    )
    return locked, True


def balance_for_plan(plan):
    """Return the due principal, net posted principal credits and outstanding principal."""
    due = DailyObligation.objects.filter(
        plan=plan,
        status="due",
        due_date__lte=timezone.localdate(),
    ).aggregate(total=Sum("amount_due"))["total"] or Decimal("0.00")
    credits = LedgerEntry.objects.filter(
        payment__plan=plan,
        category="principal",
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    return {
        "due_principal": due,
        "net_ledger_credits": credits,
        "outstanding_principal": max(due - credits, Decimal("0.00")),
    }
