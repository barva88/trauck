from django.urls import path
from . import views


app_name = "pages"

urlpatterns = [
    path('', views.index, name='index'),
    path('healthz/', views.healthz, name='healthz'),
    path('readiness/', views.readiness, name='readiness'),
]
