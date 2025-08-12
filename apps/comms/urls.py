from django.urls import path
from . import views

app_name = 'comms'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('create-web-call/', views.create_web_call, name='create_web_call'),
    # Chat endpoints (MVP placeholder)
    path('open-web-chat/', views.open_web_chat, name='open_web_chat'),
    path('send-web-chat/', views.send_web_chat, name='send_web_chat'),
]
