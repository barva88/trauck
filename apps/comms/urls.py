from django.urls import path
from . import views
from .views_webhooks import RetellWebhookView

app_name = 'comms'

urlpatterns = [
    path('', views.list_comms, name='inbox'),
    path('list/', views.list_comms, name='list'),
    path('detail/<int:pk>/', views.detail_comm, name='detail'),
    path('create-web-call/', views.create_web_call, name='create_web_call'),
    # Chat endpoints (MVP placeholder)
    path('open-web-chat/', views.open_web_chat, name='open_web_chat'),
    path('send-web-chat/', views.send_web_chat, name='send_web_chat'),
    path('debug/', views.debug, name='debug'),
    path('webhook/retell/', RetellWebhookView.as_view(), name='retell_webhook'),
]
