from django.conf import settings
import stripe
from django.contrib.auth import get_user_model
from apps.billing.models import Plan

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
print('USING_STRIPE_KEY_OK' if stripe.api_key else 'NO_STRIPE_KEY')

User = get_user_model()
user = User.objects.filter(is_active=True).first()
print('USER_EMAIL', getattr(user, 'email', None))

plan = Plan.objects.first()
print('PLAN_PRICE_ID', getattr(plan, 'stripe_price_id', None))

if not (stripe.api_key and user and plan and plan.stripe_price_id):
    print('MISSING_REQUIREMENT')
else:
    sess = stripe.checkout.Session.create(
        customer_email=user.email,
        line_items=[{'price': plan.stripe_price_id, 'quantity': 1}],
        mode='payment',
        success_url='http://localhost:8000/success',
        cancel_url='http://localhost:8000/cancel',
    )
    print('CHECKOUT_SESSION_URL', sess.url)
