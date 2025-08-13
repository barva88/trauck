from django.db import models
from django.conf import settings
import uuid


class Communication(models.Model):
    # Backward-compat types kept temporarily
    TYPE_CALL = 'call'
    TYPE_CHAT = 'chat'
    TYPE_CHOICES = (
        (TYPE_CALL, 'Call'),
        (TYPE_CHAT, 'Chat'),
    )

    # New: stable UUID (not PK yet to avoid breaking existing data)
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)

    # Existing
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='communications'
    )

    # Back-compat fields used by existing UI
    comm_type = models.CharField(max_length=10, choices=TYPE_CHOICES, blank=True)
    external_id = models.CharField(max_length=128, db_index=True)

    # New schema fields
    CHANNEL_WEB = 'web'
    CHANNEL_PHONE = 'phone'
    CHANNEL_WHATSAPP = 'whatsapp'
    CHANNEL_CHAT = 'chat'
    CHANNEL_CHOICES = (
        (CHANNEL_WEB, 'Web'),
        (CHANNEL_PHONE, 'Phone'),
        (CHANNEL_WHATSAPP, 'WhatsApp'),
        (CHANNEL_CHAT, 'Chat'),
    )
    channel = models.CharField(max_length=16, choices=CHANNEL_CHOICES, default=CHANNEL_CHAT)
    conversation_id = models.CharField(max_length=128, db_index=True, blank=True, default='')
    agent_id = models.CharField(max_length=128, blank=True, default='')
    language = models.CharField(max_length=16, default='es')

    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)

    summary = models.TextField(blank=True, null=True)

    # Token accounting
    tokens = models.IntegerField(null=True, blank=True)
    tokens_input = models.IntegerField(null=True, blank=True)
    tokens_output = models.IntegerField(null=True, blank=True)
    tokens_total = models.IntegerField(null=True, blank=True)

    source = models.CharField(max_length=32, default='retell')
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-started_at', '-created_at')
        indexes = [
            models.Index(fields=['external_id']),
            models.Index(fields=['comm_type', 'started_at']),
            models.Index(fields=['conversation_id']),
            models.Index(fields=['agent_id']),
        ]

    def __str__(self):
        label = self.channel or self.comm_type or 'comm'
        return f"{label} {self.conversation_id or self.external_id}"


class CommsMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    communication = models.ForeignKey(Communication, on_delete=models.CASCADE, related_name='messages')
    message_id = models.CharField(max_length=128, db_index=True)
    role = models.CharField(max_length=16)  # user|assistant
    text = models.TextField()
    timestamp = models.DateTimeField()
    nlp = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('timestamp', 'created_at')
        indexes = [
            models.Index(fields=['message_id']),
        ]


class CommsEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    communication = models.ForeignKey(Communication, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=64)
    payload = models.JSONField(default=dict, blank=True)
    idempotency_key = models.CharField(max_length=255, unique=True, db_index=True)
    trace_id = models.CharField(max_length=128, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created_at',)
