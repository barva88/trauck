from django.conf import settings
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings.dev')
django.setup()
from apps.billing.models import Plan, Purchase
from django.contrib.auth import get_user_model
User = get_user_model()
print('PLANS:')
for p in Plan.objects.all():
    print(p.id, p.name, 'price_usd=', p.price_usd, 'credits_on_purchase=', p.credits_on_purchase, 'stripe_price_id=', p.stripe_price_id)
print('\nPURCHASES:')
for p in Purchase.objects.all():
    print(p.id, 'user=', getattr(p.user,'email',None), 'plan_id=', getattr(p.plan,'id',None), 'credits_granted=', p.credits_granted, 'amount_usd=', p.amount_usd, 'status=', p.status, 'checkout_session_id=', p.checkout_session_id)
print('\nWALLETS:')
for u in User.objects.filter(is_active=True):
    w = getattr(u,'credit_wallet',None)
    print('user',u.email,'wallet', w.balance if w else None)
