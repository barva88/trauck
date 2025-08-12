from django.urls import path

from . import views


app_name = "accounts"

urlpatterns = [
    path('', views.index, name='index'),
    path('me', views.me_api, name='me_api'),
]
