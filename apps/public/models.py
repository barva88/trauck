from django.db import models
from django.utils.translation import gettext_lazy as _


class Timestamped(models.Model):
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("order", "-created_at")


class SiteSettings(models.Model):
    brand_name = models.CharField(max_length=150, default="Trauck")
    tagline = models.CharField(max_length=200, blank=True, default="The Smart Dispatcher for Carriers")
    hero_title = models.CharField(max_length=200, blank=True, default="Prepárate para tu CDL con Trauck")
    hero_subtitle = models.TextField(blank=True, default="Simulacros, analítica y asistencia por IA")
    primary_cta_text = models.CharField(max_length=100, blank=True, default="Comienza tu preparación CDL")
    primary_cta_url = models.URLField(blank=True, default="/auth/signup/")
    secondary_cta_text = models.CharField(max_length=100, blank=True, default="Saber más")
    secondary_cta_url = models.URLField(blank=True, default="#features")

    logo = models.ImageField(upload_to="public/", blank=True, null=True)
    logo_dark = models.ImageField(upload_to="public/", blank=True, null=True)
    favicon = models.ImageField(upload_to="public/", blank=True, null=True)

    footer_html = models.TextField(blank=True, default="© Trauck")
    contact_email = models.EmailField(blank=True, default="support@trauck.com")
    contact_phone = models.CharField(max_length=50, blank=True, default="")

    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.CharField(max_length=255, blank=True)
    og_image = models.ImageField(upload_to="public/", blank=True, null=True)
    twitter_card = models.CharField(max_length=50, blank=True, default="summary_large_image")

    def __str__(self):
        return self.brand_name


class HeroBlock(Timestamped):
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.TextField(blank=True)
    image = models.ImageField(upload_to="public/", blank=True, null=True)
    video_url = models.URLField(blank=True)
    overlay = models.BooleanField(default=True)

    def __str__(self):
        return self.title or "Hero"


class Feature(Timestamped):
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=255, blank=True)
    icon_class = models.CharField(max_length=100, blank=True, help_text=_("FontAwesome/Lucide CSS class"))
    image = models.ImageField(upload_to="public/", blank=True, null=True)

    def __str__(self):
        return self.title


class PricingPlan(Timestamped):
    name = models.CharField(max_length=100)
    price_month = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    price_annual = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    badge = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    features = models.JSONField(default=list, blank=True)
    cta_text = models.CharField(max_length=100, blank=True, default="Comenzar")
    cta_url = models.URLField(blank=True, default="/auth/signup/")
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Testimonial(Timestamped):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to="public/", blank=True, null=True)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    company = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"{self.name} — {self.company}" if self.company else self.name


class FAQ(Timestamped):
    question = models.CharField(max_length=200)
    answer = models.TextField()

    def __str__(self):
        return self.question


class PartnerLogo(Timestamped):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to="public/", blank=True, null=True)
    url = models.URLField(blank=True)

    def __str__(self):
        return self.name


class SEOPage(Timestamped):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    meta_description = models.CharField(max_length=255, blank=True)
    keywords = models.CharField(max_length=255, blank=True)
    noindex = models.BooleanField(default=False)
    canonical_url = models.URLField(blank=True)

    def __str__(self):
        return self.slug


class CTASection(Timestamped):
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    cta_text = models.CharField(max_length=100, blank=True)
    cta_url = models.URLField(blank=True)

    def __str__(self):
        return self.title


class MediaBlock(Timestamped):
    title = models.CharField(max_length=150, blank=True)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to="public/", blank=True, null=True)
    video_url = models.URLField(blank=True)
    align = models.CharField(max_length=10, choices=[("left","Left"),("right","Right")], default="left")

    def __str__(self):
        return self.title or "Media"
