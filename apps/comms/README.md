# Comms module

Retell webhook endpoint:
- URL: /comms/webhook/retell/
- Method: POST
- Auth: HMAC-SHA256 in header X-Signature using RETELL_WEBHOOK_SECRET.
- Response: {"ok": true} or {"ok": true, "duplicate": true} within ~2s.

Minimal payload example:
{
  "source": "retell",
  "version": "1",
  "event": "message_created",
  "conversation": {
    "conversation_id": "conv-123",
    "agent_id": "agent-1",
    "channel": "chat",
    "language": "es"
  },
  "message": {
    "message_id": "m-1",
    "role": "user",
    "text": "hola",
    "timestamp_iso": "2024-01-01T00:00:00Z"
  },
  "meta": {"idempotency_key": "k-123", "trace_id": "t-1"}
}

Notes:
- Idempotency enforced via meta.idempotency_key (unique).
- Messages stored in CommsMessage; events in CommsEvent.
- Communication upserted by conversation_id; ended_at set on conversation_closed/call_ended.
