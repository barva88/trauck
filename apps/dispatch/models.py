from django.db import models

# Create your models here.
from django.db import models
from apps.loads.models import Load
from apps.drivers.models import Driver

class Dispatch(models.Model):
    load = models.ForeignKey(Load, related_name='dispatches', on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, related_name='dispatches', on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    rating = models.PositiveIntegerField(null=True, blank=True)
    # Puedes agregar más campos

    def __str__(self):
        return f"Dispatch: {self.load} -> {self.driver}"