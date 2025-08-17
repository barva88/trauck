from django.contrib import admin
from . import models


@admin.register(models.SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("brand_name", "tagline", "contact_email")
    search_fields = ("brand_name", "tagline", "contact_email")


@admin.register(models.HeroBlock)
class HeroBlockAdmin(admin.ModelAdmin):
    list_display = ("title", "overlay", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle")


@admin.register(models.Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("title", "icon_class", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "icon_class")


@admin.register(models.PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_month", "price_annual", "is_featured", "order", "is_active")
    list_filter = ("is_featured", "is_active")
    search_fields = ("name", "description")


@admin.register(models.Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "rating", "order", "is_active")
    list_filter = ("rating", "is_active")
    search_fields = ("name", "company", "quote")


@admin.register(models.FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("question", "answer")


@admin.register(models.PartnerLogo)
class PartnerLogoAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(models.SEOPage)
class SEOPageAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "noindex", "order", "is_active")
    list_filter = ("noindex", "is_active")
    search_fields = ("slug", "title", "meta_description", "keywords")


@admin.register(models.CTASection)
class CTASectionAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle")


@admin.register(models.MediaBlock)
class MediaBlockAdmin(admin.ModelAdmin):
    list_display = ("title", "align", "order", "is_active")
    list_filter = ("align", "is_active")
    search_fields = ("title", "text")
