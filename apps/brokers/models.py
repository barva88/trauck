from django.db import models

class Broker(models.Model):
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    is_verified = models.BooleanField(default=False)  # Nuevo campo

    def __str__(self):
        return self.name

    @property
    def loads_count(self):
        return self.loads.count()
