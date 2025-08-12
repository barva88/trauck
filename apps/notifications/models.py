from django.db import models

# Create your models here.
from django.db import models
from apps.accounts.models import User

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('internal', 'Internal'),
    ]
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    # Puedes agregar más campos

    def __str__(self):
        return f"{self.notification_type} - {self.user.username}"