from django.db import models

# Create your models here.
from django.db import models
from apps.carriers.models import Carrier

# class Broker(models.Model):
#     name = models.CharField(max_length=255)
#     contact = models.CharField(max_length=255, blank=True)
#     phone = models.CharField(max_length=20, blank=True)
#     email = models.EmailField(blank=True)

#     def __str__(self):
#         return self.name

class Load(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    # broker = models.ForeignKey(Broker, related_name='loads', on_delete=models.CASCADE)
    broker = models.ForeignKey('brokers.Broker', related_name='loads', on_delete=models.CASCADE)
    carrier = models.ForeignKey(Carrier, related_name='loads', on_delete=models.SET_NULL, null=True, blank=True)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    pickup_date = models.DateField()
    delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    # Puedes agregar más campos

    def __str__(self):
        return f"{self.origin} -> {self.destination} ({self.status})"