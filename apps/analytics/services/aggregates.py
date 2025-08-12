from datetime import date, timedelta
from django.db.models import Sum, Count
from django.utils import timezone
from apps.billing.models import Purchase, CreditTransaction, ConsumptionEvent
from ..models import DailyRevenueFact, DailyCreditsFact


def build_revenue_for_day(d: date):
    qs_paid = Purchase.objects.filter(status=Purchase.STATUS_PAID, created_at__date=d)
    revenue = qs_paid.aggregate(total=Sum('amount_usd'))['total'] or 0
    refunds = Purchase.objects.filter(status=Purchase.STATUS_REFUNDED, created_at__date=d).aggregate(total=Sum('amount_usd'))['total'] or 0
    DailyRevenueFact.objects.update_or_create(date=d, defaults={
        'revenue': revenue,
        'refunds': refunds,
        # campos extra (mrr, arr, etc.) se rellenarán en iteraciones siguientes
    })


def build_credits_for_day(d: date):
    granted = CreditTransaction.objects.filter(created_at__date=d, type__in=['PURCHASE','SUBSCRIPTION_RENEWAL']).aggregate(total=Sum('signed_amount'))['total'] or 0
    consumed = ConsumptionEvent.objects.filter(created_at__date=d).aggregate(total=Sum('credits_spent'))['total'] or 0
    DailyCreditsFact.objects.update_or_create(date=d, defaults={
        'credits_granted': int(granted or 0),
        'credits_consumed': int(consumed or 0),
    })


def build_range(from_dt: date, to_dt: date):
    cur = from_dt
    while cur <= to_dt:
        build_revenue_for_day(cur)
        build_credits_for_day(cur)
        cur += timedelta(days=1)
