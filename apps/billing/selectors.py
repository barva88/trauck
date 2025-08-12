from .models import Plan, CreditWallet


def active_plans():
    return Plan.objects.filter(is_active=True).order_by('price_usd')


def get_wallet_for_user(user):
    from django.db import transaction
    with transaction.atomic():
        wallet, _ = CreditWallet.objects.select_for_update().get_or_create(user=user)
    return wallet
