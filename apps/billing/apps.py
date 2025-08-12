from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.billing'

    def ready(self):
        # Connect signals
        from django.contrib.auth import get_user_model
        from django.db.models.signals import post_save
        from .signals import create_user_wallet
        post_save.connect(create_user_wallet, sender=get_user_model(), dispatch_uid='billing_create_user_wallet')
