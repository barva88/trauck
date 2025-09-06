from django.contrib import admin
from .models import Plan, PlanBenefit, CreditWallet, CreditTransaction, Purchase, GuaranteeWindow, RefundRequest, ServiceType, ConsumptionEvent, CreditPack


class PlanBenefitInline(admin.TabularInline):
    model = PlanBenefit
    extra = 1

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name','is_active','price_usd','renewal_interval','credits_on_purchase')
    list_filter = ('is_active','renewal_interval')
    inlines = [PlanBenefitInline]

    def save_model(self, request, obj, form, change):
        # Prevent creating paid plans with zero credits via admin
        try:
            price = float(obj.price_usd or 0)
        except Exception:
            price = 0
        if price > 0 and (not obj.credits_on_purchase or obj.credits_on_purchase <= 0):
            obj.credits_on_purchase = 1  # sensible default to avoid zero-credit paid plan
        super().save_model(request, obj, form, change)

@admin.register(CreditWallet)
class CreditWalletAdmin(admin.ModelAdmin):
    list_display = ('user','balance','created_at','updated_at')

@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet','type','signed_amount','reason','created_at')
    list_filter = ('type',)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id','user','status','credits_granted','amount_usd','created_at')
    list_filter = ('status',)
    actions = []

@admin.register(GuaranteeWindow)
class GuaranteeWindowAdmin(admin.ModelAdmin):
    list_display = ('purchase','status','start','end')

@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ('purchase','user','status','refund_amount_usd','created_at')
    list_filter = ('status',)

@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('code','label','default_cost_credits')

@admin.register(ConsumptionEvent)
class ConsumptionEventAdmin(admin.ModelAdmin):
    list_display = ('wallet','service_type','credits_spent','created_at')

@admin.register(CreditPack)
class CreditPackAdmin(admin.ModelAdmin):
    list_display = ('name','credits','price_usd','is_active')
