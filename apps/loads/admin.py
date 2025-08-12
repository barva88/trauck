from django.contrib import admin

# Register your models here.

from .models import Load

class LoadAdmin(admin.ModelAdmin):
    list_display = ('origin', 'destination', 'pickup_date', 'delivery_date', 'status', 'rate')
    search_fields = ('origin', 'destination', 'status')
    list_filter = ('status', 'pickup_date', 'delivery_date')

admin.site.register(Load, LoadAdmin)