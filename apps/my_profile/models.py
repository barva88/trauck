from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    external_id = models.CharField(max_length=255, blank=True, null=True, unique=True, db_index=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"