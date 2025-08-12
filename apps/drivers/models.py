from django.db import models

# Create your models here.
from django.db import models
from apps.carriers.models import Carrier

class Driver(models.Model):
    carrier = models.ForeignKey(Carrier, related_name='drivers', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    # Puedes agregar más campos

    def __str__(self):
        return self.name