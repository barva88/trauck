from django.urls import path

from . import views


app_name = "carriers"

urlpatterns = [
    path('', views.index, name='index'),
]
