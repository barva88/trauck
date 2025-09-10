from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django_hosts.resolvers import reverse

class AccountAdapter(DefaultAccountAdapter):
    def confirm_email(self, request, email_address):
        user = email_address.user
        super().confirm_email(request, email_address)
        # Crear Stripe customer al confirmar el email (primera vez)
        try:
            from apps.my_profile.models import Profile
            prof, _ = Profile.objects.get_or_create(user=user)
            if not prof.stripe_customer_id:
                from apps.billing.services.stripe_service import get_or_create_stripe_customer
                get_or_create_stripe_customer(user)
        except Exception:
            # No bloquear la confirmación por errores externos
            pass

    def get_login_redirect_url(self, request):
        # Prefer a host-aware URL to the dashboard index when running with a
        # configured PARENT_HOST so redirects after login/registration end up
        # on the dashboard subdomain. Fall back to a relative path for dev.
        parent = getattr(settings, 'PARENT_HOST', None)
        if parent:
            try:
                return reverse('pages:index', host='dashboard')
            except Exception:
                return f"{getattr(settings,'HOST_SCHEME','https://')}dashboard.{parent}/"
        return '/'

    def get_signup_redirect_url(self, request):
        return self.get_login_redirect_url(request)
