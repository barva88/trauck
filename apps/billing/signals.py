from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import CreditWallet


@receiver(post_save, sender=get_user_model())
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        CreditWallet.objects.get_or_create(user=instance)
