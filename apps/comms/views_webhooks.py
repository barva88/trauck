from django.utils import timezone
from django.db import transaction, IntegrityError
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import hashlib, hmac, json
from .models import Communication, CommsEvent, CommsMessage
from .serializers import RetellWebhookSerializer
from datetime import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


def _parse_iso(ts: str):
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.utc)
        return dt
    except Exception:
        return None


def _verify_signature(raw_body: bytes, header_sig: str) -> bool:
    secret = getattr(settings, 'RETELL_WEBHOOK_SECRET', '')
    if not secret:
        return True  # not enforced
    try:
        mac = hmac.new(secret.encode('utf-8'), msg=raw_body, digestmod=hashlib.sha256)
        expected = mac.hexdigest()
        return hmac.compare_digest(expected, (header_sig or ''))
    except Exception:
        return False


@method_decorator(csrf_exempt, name='dispatch')
class RetellWebhookView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = []

    def post(self, request):
        raw = request.body or b''
        sig = request.headers.get('X-Signature') or request.headers.get('X-Retell-Signature')
        if not _verify_signature(raw, sig):
            return Response({'ok': False, 'error': 'invalid_signature'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            data = json.loads(raw.decode('utf-8') or '{}')
        except Exception:
            return Response({'ok': False, 'error': 'invalid_json'}, status=status.HTTP_400_BAD_REQUEST)

        ser = RetellWebhookSerializer(data=data)
        if not ser.is_valid():
            return Response({'ok': False, 'error': ser.errors}, status=status.HTTP_400_BAD_REQUEST)
        payload = ser.validated_data

        meta = payload.get('meta') or {}
        idem_key = meta.get('idempotency_key')
        trace_id = meta.get('trace_id')
        convo = payload['conversation']
        event = payload['event']
        message = payload.get('message')
        nlp = payload.get('nlp') or {}

        # Optional allowlist of agent IDs
        allow = getattr(settings, 'RETELL_ALLOWED_AGENT_IDS', '') or ''
        if allow.strip():
            allowed = {a.strip() for a in allow.split(',') if a.strip()}
            if allowed and convo.get('agent_id') not in allowed:
                return Response({'ok': True, 'ignored': 'agent_not_allowed'})

        # Idempotency: insert event record first
        try:
            with transaction.atomic():
                comm = Communication.objects.filter(conversation_id=convo['conversation_id']).first()
                if not comm:
                    comm = Communication.objects.create(
                        external_id=convo['conversation_id'],
                        comm_type=(Communication.TYPE_CHAT if (convo.get('channel') or 'chat') == 'chat' else Communication.TYPE_CALL),
                        channel=convo.get('channel') or 'chat',
                        conversation_id=convo['conversation_id'],
                        agent_id=convo.get('agent_id', ''),
                        language=convo.get('language') or 'es',
                        started_at=timezone.now(),
                        metadata={'source': payload.get('source') or 'retell'}
                    )

                CommsEvent.objects.create(
                    communication=comm,
                    event_type=event,
                    payload=data,
                    idempotency_key=idem_key,
                    trace_id=trace_id,
                )
        except IntegrityError:
            # Duplicate idem_key
            return Response({'ok': True, 'duplicate': True})

        # Update communication fields based on event
        updates = []
        if event == 'message_created' and message:
            ts = message.get('timestamp_iso')
            ts_dt = _parse_iso(ts) or timezone.now()
            CommsMessage.objects.create(
                communication=comm,
                message_id=message.get('message_id', ''),
                role=message.get('role', ''),
                text=message.get('text', ''),
                timestamp=ts_dt,
                nlp=nlp or {},
            )
        elif event in ('conversation_started', 'call_started'):
            if not comm.started_at:
                comm.started_at = timezone.now()
                updates.append('started_at')
        elif event in ('conversation_closed', 'call_ended', 'conversation_ended'):
            if not comm.ended_at:
                comm.ended_at = timezone.now()
                updates.append('ended_at')

        # Token usage, summary from optional fields
        usage = data.get('usage') or {}
        if usage.get('prompt_tokens') is not None:
            comm.tokens_input = int(usage.get('prompt_tokens'))
            updates.append('tokens_input')
        if usage.get('completion_tokens') is not None:
            comm.tokens_output = int(usage.get('completion_tokens'))
            updates.append('tokens_output')
        if usage.get('total_tokens') is not None:
            comm.tokens_total = int(usage.get('total_tokens'))
            updates.append('tokens_total')

        summary = data.get('summary')
        if isinstance(summary, dict):
            summary = summary.get('text')
        if isinstance(summary, str) and summary:
            comm.summary = summary
            updates.append('summary')

        if updates:
            comm.save(update_fields=list(set(updates + ['updated_at'])))

        return Response({'ok': True})
