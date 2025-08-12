from django.contrib import admin
from .models import Carrier

@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ('name',  'phone', 'email')
    search_fields = ('name', 'email')