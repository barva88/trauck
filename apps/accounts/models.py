from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Puedes agregar campos personalizados aquí
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('dispatcher', 'Dispatcher'),
        ('driver', 'Driver'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='driver')
    # Modifica los roles según tus necesidades

    def __str__(self):
        return self.username