from django.db import models

# Create your models here.
from django.db import models

class Carrier(models.Model):
    name = models.CharField(max_length=255)
    dot_number = models.CharField(max_length=50, unique=True)
    mc_number = models.CharField(max_length=50, unique=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    # Agrega más campos si lo necesitas

    def __str__(self):
        return self.name