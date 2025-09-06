import stripe
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from ..models import Purchase, Plan, CreditPack, CreditTransaction, GuaranteeWindow, RefundRequest, ConsumptionEvent, ServiceType
from ..selectors import get_wallet_for_user

try:
    from apps.notifications.models import Notification
except Exception:
    Notification = None

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
stripe.api_version = '2024-06-20'


def _ensure_stripe_key():
    if not getattr(stripe, 'api_key', None):
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
    if not stripe.api_key:
        raise ValueError('Stripe secret key not configured')


def get_or_create_stripe_customer(user):
    profile = getattr(user, 'profile', None) or getattr(user, 'my_profile', None)
    # We expect stripe_customer_id on profile if exists
    stripe_customer_id = getattr(profile, 'stripe_customer_id', None)
    if not stripe_customer_id:
        _ensure_stripe_key()
        customer = stripe.Customer.create(email=user.email or None, name=user.get_username())
        if profile and hasattr(profile, 'stripe_customer_id'):
            profile.stripe_customer_id = customer.id
            profile.save(update_fields=['stripe_customer_id'])
        return customer.id
    return stripe_customer_id


# New: make sure a Billing Portal configuration exists in test mode
# If a configuration id is provided in settings, use it; otherwise try to reuse an existing
# configuration or create a minimal one on the fly.
def _get_or_create_portal_configuration_id():
    _ensure_stripe_key()
    cfg_id = getattr(settings, 'STRIPE_PORTAL_CONFIGURATION_ID', '')
    # If provided, verify it exists
    if cfg_id:
        try:
            cfg = stripe.billing_portal.Configuration.retrieve(cfg_id)
            return cfg.id
        except Exception:
            # fall through to auto-detect
            pass
    # Try to reuse any existing active configuration
    try:
        lst = stripe.billing_portal.Configuration.list(limit=1)
        if lst and getattr(lst, 'data', None):
            return lst.data[0].id
    except Exception:
        pass
    # Create a minimal configuration if nothing exists
    try:
        cfg = stripe.billing_portal.Configuration.create(
            business_profile={
                # This can be adjusted in Dashboard later
                'headline': getattr(settings, 'DEFAULT_FROM_EMAIL', 'Customer Portal'),
            },
            features={
                'invoice_history': {'enabled': True},
                'payment_method_update': {'enabled': True},
                'customer_update': {
                    'enabled': True,
                    'allowed_updates': ['address', 'email', 'name', 'phone'],
                },
                'subscription_cancel': {'enabled': True},
            },
        )
        return cfg.id
    except Exception:
        # As a last resort, return None and let Session.create try without configuration
        return None


def create_checkout_session(user, plan_or_pack, success_url, cancel_url, mode='payment'):
    # plan_or_pack can be Plan or CreditPack
    price_id = getattr(plan_or_pack, 'stripe_price_id', None)
    if not price_id:
        raise ValueError('Stripe price not configured')
    _ensure_stripe_key()
    customer_id = get_or_create_stripe_customer(user)

    # Ensure we get session_id back on success
    placeholder = '{CHECKOUT_SESSION_ID}'
    if 'session_id=' not in success_url:
        sep = '&' if '?' in success_url else '?'
        success_url = f"{success_url}{sep}session_id={placeholder}"

    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode=mode,
        line_items=[{'price': price_id, 'quantity': 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            'user_id': str(user.id),
            'plan_id': str(getattr(plan_or_pack, 'id', '') ),
            'object_type': plan_or_pack.__class__.__name__,
        }
    )

    from ..models import Plan
    p = Purchase.objects.create(
        user=user,
        plan=plan_or_pack if isinstance(plan_or_pack, Plan) else None,
        credit_pack=plan_or_pack if isinstance(plan_or_pack, CreditPack) else None,
        stripe_product_id=getattr(plan_or_pack, 'stripe_product_id', None),
        stripe_price_id=price_id,
        checkout_session_id=session.id,
        status=Purchase.STATUS_PENDING,
        amount_usd=getattr(plan_or_pack, 'price_usd', 0),
        credits_granted=getattr(plan_or_pack, 'credits_on_purchase', getattr(plan_or_pack, 'credits', 0))
    )

    return session.url, p


def complete_checkout_by_session_id(session_id: str):
    """Fallback local: si no llegan webhooks, completar la compra desde el success_url."""
    _ensure_stripe_key()
    session = stripe.checkout.Session.retrieve(session_id)
    # Simular evento de webhook para reutilizar la lógica
    handle_checkout_completed({'data': {'object': session.to_dict()}})
    return True


def create_billing_portal_session(user, return_url=None):
    _ensure_stripe_key()
    customer_id = get_or_create_stripe_customer(user)
    return_url = return_url or getattr(settings, 'STRIPE_PORTAL_RETURN_URL', '/')
    # Try to ensure a configuration exists
    cfg_id = _get_or_create_portal_configuration_id()
    kwargs = {'customer': customer_id, 'return_url': return_url}
    if cfg_id:
        kwargs['configuration'] = cfg_id
    try:
        portal = stripe.billing_portal.Session.create(**kwargs)
    except Exception as e:
        # Retry once if configuration is missing on the account
        msg = str(e)
        if 'No configuration provided' in msg or 'default configuration has not been created' in msg:
            cfg_id = _get_or_create_portal_configuration_id()
            if cfg_id:
                kwargs['configuration'] = cfg_id
                portal = stripe.billing_portal.Session.create(**kwargs)
            else:
                raise
        else:
            raise
    return portal.url


def _credit_wallet(user, credits: int, reason: str, metadata: dict):
    wallet = get_wallet_for_user(user)
    wallet.balance += credits
    wallet.save(update_fields=['balance', 'updated_at'])
    CreditTransaction.objects.create(wallet=wallet, type=CreditTransaction.TYPE_PURCHASE, signed_amount=credits, reason=reason, metadata=metadata)
    return wallet


def handle_checkout_completed(event):
    data = event['data']['object']
    session_id = data.get('id')
    try:
        purchase = Purchase.objects.get(checkout_session_id=session_id)
    except Purchase.DoesNotExist:
        return
    if purchase.status == Purchase.STATUS_PAID:
        return
    purchase.status = Purchase.STATUS_PAID
    purchase.payment_intent_id = data.get('payment_intent')
    purchase.subscription_id = data.get('subscription')
    purchase.save(update_fields=['status','payment_intent_id','subscription_id','updated_at'])

    # Asegurar créditos al pagar
    # Si por alguna razón purchase.credits_granted es 0 (por ejemplo plan creado sin créditos),
    # recalcular desde el plan y acreditar la cantidad adecuada.
    credits_expected = 0
    if purchase.plan:
        credits_expected = int(getattr(purchase.plan, 'credits_on_purchase', 0) or 0)
    elif purchase.credit_pack:
        credits_expected = int(getattr(purchase.credit_pack, 'credits', 0) or 0)

    # If purchase.credits_granted is zero, update it to the expected value
    if not purchase.credits_granted and credits_expected > 0:
        purchase.credits_granted = credits_expected
        purchase.save(update_fields=['credits_granted','updated_at'])

    # Determine how many credits to actually grant (could be 0 if already granted earlier)
    to_grant = int(purchase.credits_granted or 0)
    if to_grant > 0:
        _credit_wallet(purchase.user, to_grant, 'Checkout completed', {'purchase_id': purchase.id})
    purchase.open_guarantee()


def handle_invoice_paid(event):
    data = event['data']['object']
    sub_id = data.get('subscription')
    try:
        purchase = Purchase.objects.get(subscription_id=sub_id)
    except Purchase.DoesNotExist:
        return
    credits = purchase.plan.credits_on_purchase if purchase.plan else 0
    _credit_wallet(purchase.user, credits, 'Subscription renewal', {'purchase_id': purchase.id, 'invoice_id': data.get('id')})
    purchase.open_guarantee()


def handle_payment_failed(event):
    data = event['data']['object']
    sub_id = data.get('subscription')
    try:
        purchase = Purchase.objects.get(subscription_id=sub_id)
    except Purchase.DoesNotExist:
        return
    purchase.status = Purchase.STATUS_PAST_DUE
    purchase.save(update_fields=['status','updated_at'])
    if Notification:
        try:
            portal_url = reverse('billing:portal_open')
        except Exception:
            portal_url = '#'
        Notification.objects.create(
            user=purchase.user,
            message=f'Tu pago de suscripción ha fallado. Actualiza tu método de pago aquí: {portal_url}',
            notification_type='internal'
        )
    return


def _used_credits_during_guarantee(purchase: Purchase) -> int:
    # Prefer purchases linked in consumption, else fallback by time window
    qs = ConsumptionEvent.objects.filter(wallet__user=purchase.user, purchase=purchase)
    if not qs.exists() and purchase.guarantee_starts_at and purchase.guarantee_ends_at:
        qs = ConsumptionEvent.objects.filter(
            wallet__user=purchase.user,
            created_at__gte=purchase.guarantee_starts_at,
            created_at__lte=purchase.guarantee_ends_at
        )
    return sum(c.credits_spent for c in qs)


def request_refund(user, purchase: Purchase, amount=None):
    # Validación de garantía y consumo + posible prorrata
    now = timezone.now()
    if purchase.user_id != user.id:
        raise ValueError('Invalid user')
    if not purchase.guarantee_ends_at or purchase.guarantee_ends_at < now:
        raise ValueError('Guarantee window expired')

    used = _used_credits_during_guarantee(purchase)
    threshold = int(getattr(settings, 'BILLING_ALLOW_REFUND_IF_USED_THRESHOLD', 0))
    pro_rata = bool(getattr(settings, 'BILLING_REFUND_PRO_RATA', False))

    if used == 0:
        refund_amount = purchase.amount_usd
    elif pro_rata and purchase.credits_granted > 0 and purchase.amount_usd:
        ratio = max(0, (purchase.credits_granted - used) / purchase.credits_granted)
        refund_amount = round(float(purchase.amount_usd) * ratio, 2)
    elif used <= threshold:
        refund_amount = purchase.amount_usd
    else:
        raise ValueError('Refund not eligible due to usage')

    # Intentar Stripe refund si hay payment_intent_id y clave
    refund_id = None
    try:
        _ensure_stripe_key()
        if purchase.payment_intent_id:
            cents = int(round(float(refund_amount) * 100))
            r = stripe.Refund.create(payment_intent=purchase.payment_intent_id, amount=cents)
            refund_id = r.id
    except Exception:
        # fallback a registro interno
        refund_id = None

    RefundRequest.objects.create(
        purchase=purchase,
        user=user,
        reason_text='Guarantee refund',
        refund_amount_usd=refund_amount,
        stripe_refund_id=refund_id,
        status=RefundRequest.STATUS_COMPLETED if refund_id else RefundRequest.STATUS_APPROVED
    )
    purchase.status = Purchase.STATUS_REFUNDED
    purchase.save(update_fields=['status','updated_at'])
    if hasattr(purchase, 'guarantee'):
        purchase.guarantee.status = GuaranteeWindow.STATUS_REFUNDED
        purchase.guarantee.save(update_fields=['status'])
    return refund_amount


def _ensure_service_type(code: str) -> ServiceType:
    default_cost = int(getattr(settings, 'BILLING_DEFAULT_EXAM_COST_CREDITS', 1)) if code == 'exam' else 1
    st, _ = ServiceType.objects.get_or_create(
        code=code,
        defaults={'label': code.capitalize(), 'default_cost_credits': default_cost}
    )
    return st


def debit_credits(user, service_code: str, amount_credits: int, source_metadata=None):
    st = _ensure_service_type(service_code)
    wallet = get_wallet_for_user(user)
    wallet.debit(amount_credits, reason=f'Consume {service_code}', metadata=source_metadata or {})
    ce = ConsumptionEvent.objects.create(
        wallet=wallet,
        service_type=st,
        credits_spent=amount_credits,
        source=(source_metadata or {}).get('source', ''),
        purchase_id=(source_metadata or {}).get('purchase_id')
    )
    return True


def current_balance(user):
    return get_wallet_for_user(user).balance


def can_consume(user, service_code: str, amount_credits: int = 1):
    return current_balance(user) >= amount_credits
