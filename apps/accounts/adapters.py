from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings

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
