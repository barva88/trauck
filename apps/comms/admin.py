from django.contrib import admin
from .models import Communication
from .models import CommsMessage, CommsEvent


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'comm_type', 'external_id', 'user', 'agent_id', 'started_at', 'duration_seconds', 'tokens_total')
    list_filter = ('comm_type', 'agent_id', 'started_at')
    search_fields = ('external_id', 'summary', 'agent_id', 'user__email')
    ordering = ('-started_at', '-created_at')


@admin.register(CommsMessage)
class CommsMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'communication', 'role', 'short_text', 'timestamp')
    list_filter = ('role',)
    search_fields = ('text', 'message_id', 'communication__external_id', 'communication__conversation_id')

    def short_text(self, obj):
        return (obj.text or '')[:80]


@admin.register(CommsEvent)
class CommsEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'communication', 'event_type', 'idempotency_key', 'created_at')
    list_filter = ('event_type',)
    search_fields = ('idempotency_key', 'trace_id', 'communication__external_id', 'communication__conversation_id')
