from django.conf import settings
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings.dev')
django.setup()
from apps.billing.models import Plan, Purchase
from apps.billing.services.stripe_service import _credit_wallet

# Configurable values
PLAN_SLUG = 'dev-plan-10-usd-linked'
DEFAULT_CREDITS = 10

print('Looking for plan with slug=', PLAN_SLUG)
try:
    plan = Plan.objects.get(slug=PLAN_SLUG)
except Plan.DoesNotExist:
    print('Plan not found')
    raise SystemExit(1)

print('Before: plan credits_on_purchase=', plan.credits_on_purchase)
if not plan.credits_on_purchase:
    plan.credits_on_purchase = DEFAULT_CREDITS
    plan.save(update_fields=['credits_on_purchase','updated_at'])
    print('Updated plan.credits_on_purchase ->', plan.credits_on_purchase)
else:
    print('Plan already has credits_on_purchase=', plan.credits_on_purchase)

# Now credit existing PAID purchases that have credits_granted == 0
q = Purchase.objects.filter(plan=plan, status=Purchase.STATUS_PAID, credits_granted__in=(0,None))
print('Found purchases to fix:', q.count())
for p in q:
    credits = int(plan.credits_on_purchase or DEFAULT_CREDITS)
    print('Processing Purchase', p.id, 'user', p.user.email, 'credits->', credits)
    _credit_wallet(p.user, credits, 'Retroactive credit for checkout', {'purchase_id': p.id})
    p.credits_granted = credits
    p.save(update_fields=['credits_granted','updated_at'])
    print('Done')

print('Completed')
