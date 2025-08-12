from django.db import models

# Create your models here.
from django.db import models
from apps.loads.models import Load

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ]
    load = models.ForeignKey(Load, related_name='payments', on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    issued_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    # Puedes agregar más campos

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.status}"