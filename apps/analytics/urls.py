from django.urls import path
from .views import dashboard_page, AnalyticsSummaryApi, AnalyticsTimeseriesApi, AnalyticsTopCustomersApi, AnalyticsPaymentsApi, AnalyticsDunningApi

app_name = 'analytics'

urlpatterns = [
    path('', dashboard_page, name='dashboard'),
    path('api/summary/', AnalyticsSummaryApi.as_view(), name='api_summary'),
    path('api/timeseries/', AnalyticsTimeseriesApi.as_view(), name='api_timeseries'),
    path('api/top-customers/', AnalyticsTopCustomersApi.as_view(), name='api_top_customers'),
    path('api/payments/', AnalyticsPaymentsApi.as_view(), name='api_payments'),
    path('api/dunning/', AnalyticsDunningApi.as_view(), name='api_dunning'),
]
