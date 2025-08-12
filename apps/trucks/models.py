from django.db import models

# Create your models here.
from django.db import models
from apps.carriers.models import Carrier

class Truck(models.Model):
    carrier = models.ForeignKey(Carrier, related_name='trucks', on_delete=models.CASCADE)
    plate_number = models.CharField(max_length=20)
    vin = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    # Puedes agregar más campos

    def __str__(self):
        return f"{self.plate_number} - {self.model}"