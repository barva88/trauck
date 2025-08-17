from django.views.generic import TemplateView
from django.shortcuts import redirect
from django_hosts.resolvers import reverse
from .models import (
    SiteSettings, HeroBlock, Feature, PricingPlan, Testimonial, FAQ, PartnerLogo, SEOPage, CTASection, MediaBlock
)


class HomeView(TemplateView):
    template_name = "public/home.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Send logged-in users to dashboard host
            try:
                url = reverse('pages:index', host='dashboard')
            except Exception:
                url = reverse('root', host='dashboard') if hasattr(self, 'host') else '/'
            return redirect(url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        settings = SiteSettings.objects.first()
        ctx["site_settings"] = settings
        ctx["hero"] = HeroBlock.objects.filter(is_active=True).order_by("order").first()
        ctx["features"] = Feature.objects.filter(is_active=True).order_by("order")[:6]
        ctx["plans"] = PricingPlan.objects.filter(is_active=True).order_by("order")
        ctx["testimonials"] = Testimonial.objects.filter(is_active=True).order_by("order")
        ctx["faqs"] = FAQ.objects.filter(is_active=True).order_by("order")
        ctx["partners"] = PartnerLogo.objects.filter(is_active=True).order_by("order")
        ctx["cta"] = CTASection.objects.filter(is_active=True).order_by("order").first()
        ctx["blocks"] = MediaBlock.objects.filter(is_active=True).order_by("order")
        return ctx
