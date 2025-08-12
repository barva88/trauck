from django.db import models

# Create your models here.
from django.db import models
from apps.loads.models import Load
from apps.carriers.models import Carrier

class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('bol', 'Bill of Lading'),
        ('pod', 'Proof of Delivery'),
        ('insurance', 'Insurance'),
        # Agrega más tipos si lo necesitas
    ]
    carrier = models.ForeignKey(Carrier, related_name='documents', on_delete=models.CASCADE, null=True, blank=True)
    load = models.ForeignKey(Load, related_name='documents', on_delete=models.CASCADE, null=True, blank=True)
    doc_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Puedes agregar más campos

    def __str__(self):
        return f"{self.doc_type} - {self.id}"