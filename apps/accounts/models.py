from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    """Small shim manager that allows create_user(email=..., password=...) by
    providing a default username when none is given. The project previously
    relied on calling create_user(email=..., password=...) in tests.
    """

    def _ensure_username(self, username, email):
        if username:
            return username
        if email:
            # use the local-part of the email as a fallback username
            return str(email).split('@', 1)[0]
        return super().make_random_password()

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        username = self._ensure_username(username, email)
        return super().create_user(username=username, email=email, password=password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        username = self._ensure_username(username, email)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return super().create_superuser(username=username, email=email, password=password, **extra_fields)


class User(AbstractUser):
    # Puedes agregar campos personalizados aquí
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('dispatcher', 'Dispatcher'),
        ('driver', 'Driver'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='driver')
    # Modifica los roles según tus necesidades

    objects = CustomUserManager()

    def __str__(self):
        return self.username