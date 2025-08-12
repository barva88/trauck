from django.urls import path
from . import views

app_name = "brokers"

urlpatterns = [
    path('', views.list_brokers, name='list'),
]