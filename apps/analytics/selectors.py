from datetime import date, timedelta
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.billing.models import Purchase, CreditTransaction, ConsumptionEvent, ServiceType
from .models import DailyRevenueFact, DailyCreditsFact

User = get_user_model()


def date_range(from_dt, to_dt):
    return from_dt, to_dt


def kpis_summary(from_dt, to_dt):
    # Si hay facts, usa facts; si no, calcula on the fly
    facts_r = DailyRevenueFact.objects.filter(date__gte=from_dt, date__lte=to_dt)
    facts_c = DailyCreditsFact.objects.filter(date__gte=from_dt, date__lte=to_dt)
    if facts_r.exists() and facts_c.exists():
        revenue = facts_r.aggregate(total=Sum('revenue'))['total'] or 0
        refunds = facts_r.aggregate(total=Sum('refunds'))['total'] or 0
        granted = facts_c.aggregate(total=Sum('credits_granted'))['total'] or 0
        consumed = facts_c.aggregate(total=Sum('credits_consumed'))['total'] or 0
    else:
        qs_p = Purchase.objects.filter(created_at__date__gte=from_dt, created_at__date__lte=to_dt, status=Purchase.STATUS_PAID)
        revenue = qs_p.aggregate(total=Sum('amount_usd'))['total'] or 0
        refunds = Purchase.objects.filter(created_at__date__gte=from_dt, created_at__date__lte=to_dt, status=Purchase.STATUS_REFUNDED).aggregate(total=Sum('amount_usd'))['total'] or 0
        granted = CreditTransaction.objects.filter(created_at__date__gte=from_dt, created_at__date__lte=to_dt, type__in=['PURCHASE','SUBSCRIPTION_RENEWAL']).aggregate(total=Sum('signed_amount'))['total'] or 0
        consumed = ConsumptionEvent.objects.filter(created_at__date__gte=from_dt, created_at__date__lte=to_dt).aggregate(total=Sum('credits_spent'))['total'] or 0

    return {
        'revenue': float(revenue),
        'refunds': float(refunds),
        'credits': {'granted': int(granted or 0), 'consumed': int(consumed or 0)},
    }


def services_breakdown(from_dt, to_dt):
    qs = ConsumptionEvent.objects.filter(created_at__date__gte=from_dt, created_at__date__lte=to_dt)
    by_service = qs.values('service_type__label').annotate(total=Sum('credits_spent')).order_by('-total')
    return [{'label': x['service_type__label'], 'value': x['total'] or 0} for x in by_service]


def timeseries(metric: str, from_dt: date, to_dt: date):
    data = []
    cur = from_dt
    while cur <= to_dt:
        if metric == 'revenue':
            val = float(Purchase.objects.filter(status=Purchase.STATUS_PAID, created_at__date=cur).aggregate(s=Sum('amount_usd'))['s'] or 0)
        elif metric == 'credits':
            val = int(ConsumptionEvent.objects.filter(created_at__date=cur).aggregate(s=Sum('credits_spent'))['s'] or 0)
        elif metric == 'loads':
            val = 0  # placeholder si no hay app loads
        elif metric == 'risk':
            val = 0  # placeholder
        else:
            val = 0
        data.append({'date': cur.isoformat(), 'value': val})
        cur += timedelta(days=1)
    return data


def top_customers(limit=10, from_dt=None, to_dt=None):
    qs = Purchase.objects.filter(status=Purchase.STATUS_PAID)
    if from_dt and to_dt:
        qs = qs.filter(created_at__date__gte=from_dt, created_at__date__lte=to_dt)
    agg = qs.values('user_id', 'user__username').annotate(revenue=Sum('amount_usd')).order_by('-revenue')[:limit]
    # credits consumed por usuario
    cons = ConsumptionEvent.objects
    if from_dt and to_dt:
        cons = cons.filter(created_at__date__gte=from_dt, created_at__date__lte=to_dt)
    cons = cons.values('wallet__user_id').annotate(consumed=Sum('credits_spent'))
    consumed_map = {x['wallet__user_id']: x['consumed'] or 0 for x in cons}
    return [
        {
            'user_id': x['user_id'],
            'username': x['user__username'],
            'revenue': float(x['revenue'] or 0),
            'credits_consumed': int(consumed_map.get(x['user_id'], 0)),
        }
        for x in agg
    ]


def list_payments(limit=50, status=None):
    qs = Purchase.objects.select_related('user').order_by('-created_at')
    if status == 'paid':
        qs = qs.filter(status=Purchase.STATUS_PAID)
    elif status == 'refunded':
        qs = qs.filter(status=Purchase.STATUS_REFUNDED)
    elif status == 'failed':
        qs = qs.filter(status=Purchase.STATUS_PAST_DUE)
    return list(qs[:limit])


def list_dunning(limit=50):
    return list(Purchase.objects.select_related('user').filter(status=Purchase.STATUS_PAST_DUE).order_by('-updated_at')[:limit])
