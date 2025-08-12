from django.contrib import admin
from .models import Broker

@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'phone', 'email', 'is_verified', 'loads_count')
    list_filter = ('is_verified',)
    search_fields = ('name', 'contact', 'email')