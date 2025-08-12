from datetime import date, timedelta, datetime
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test, login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .selectors import kpis_summary, services_breakdown, timeseries, top_customers, list_payments, list_dunning
from apps.billing.models import Purchase

is_admin = user_passes_test(lambda u: u.is_authenticated and (u.is_staff or u.is_superuser))


class AnalyticsSummaryApi(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        rng = request.GET.get('range','7d')
        to_dt = date.today()
        if rng == '7d':
            from_dt = to_dt - timedelta(days=6)
        elif rng == '30d':
            from_dt = to_dt - timedelta(days=29)
        else:
            from_dt = to_dt - timedelta(days=6)
        data = kpis_summary(from_dt, to_dt)
        data = {
            'revenue': {'total': data['revenue']},
            'credits': data['credits'],
        }
        return Response(data)


class AnalyticsTimeseriesApi(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        metric = request.GET.get('metric', 'revenue')
        rng = request.GET.get('range','7d')
        to_dt = date.today()
        from_dt = to_dt - timedelta(days=6) if rng == '7d' else to_dt - timedelta(days=29)
        data = timeseries(metric, from_dt, to_dt)
        return Response({'metric': metric, 'points': data})


class AnalyticsTopCustomersApi(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        rng = request.GET.get('range','7d')
        to_dt = date.today()
        from_dt = to_dt - timedelta(days=6) if rng == '7d' else to_dt - timedelta(days=29)
        limit = int(request.GET.get('limit', 10))
        data = top_customers(limit=limit, from_dt=from_dt, to_dt=to_dt)
        return Response({'results': data})


class AnalyticsPaymentsApi(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        status = request.GET.get('status')
        limit = int(request.GET.get('limit', 50))
        qs = list_payments(limit=limit, status=status)
        results = [
            {
                'id': p.id,
                'created_at': p.created_at,
                'user': str(p.user),
                'amount_usd': float(p.amount_usd or 0),
                'status': p.status,
            }
            for p in qs
        ]
        return Response({'results': results})


class AnalyticsDunningApi(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        limit = int(request.GET.get('limit', 50))
        qs = list_dunning(limit=limit)
        results = [
            {
                'id': p.id,
                'updated_at': p.updated_at,
                'user': str(p.user),
                'amount_usd': float(p.amount_usd or 0),
                'status': p.status,
            }
            for p in qs
        ]
        return Response({'results': results})


@is_admin
def dashboard_page(request):
    rng = request.GET.get('range','7d')
    to_dt = date.today()
    from_dt = to_dt - timedelta(days=6) if rng=='7d' else to_dt - timedelta(days=29)
    summary = kpis_summary(from_dt, to_dt)
    breakdown = services_breakdown(from_dt, to_dt)
    payments = Purchase.objects.select_related('user').order_by('-created_at')[:20]
    top = top_customers(limit=10, from_dt=from_dt, to_dt=to_dt)
    dunning = list_dunning(limit=10)
    context = {
        'segment': 'analytics',
        'summary': summary,
        'breakdown': breakdown,
        'payments': payments,
        'top_customers': top,
        'dunning': dunning,
        'range': rng,
    }
    return render(request, 'analytics/dashboard.html', context)
