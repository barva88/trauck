# from django.apps import AppConfig


# class MyProfileConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'apps.my_profile'
from django.apps import AppConfig

class MyProfileConfig(AppConfig):
    name = 'apps.my_profile'

    def ready(self):
        import apps.my_profile.signals