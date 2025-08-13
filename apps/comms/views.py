from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings
from retell import Retell
import json
import requests
from .models import Communication
from datetime import datetime

def list_comms(request):
    if not request.user.is_authenticated:
        return render(request, 'account/login.html', status=401)

    qs = Communication.objects.all()
    # Basic search & filters
    q = (request.GET.get('q') or '').strip()
    comm_type = (request.GET.get('type') or '').strip()
    agent = (request.GET.get('agent') or '').strip()
    date_from = (request.GET.get('from') or '').strip()
    date_to = (request.GET.get('to') or '').strip()

    if q:
        from django.db.models import Q
        qs = qs.filter(
            Q(summary__icontains=q)
            | Q(external_id__icontains=q)
            | Q(agent_id__icontains=q)
            | Q(user__email__icontains=q)
            | Q(user__username__icontains=q)
        )
    if comm_type in (Communication.TYPE_CALL, Communication.TYPE_CHAT):
        qs = qs.filter(comm_type=comm_type)
    if agent:
        qs = qs.filter(agent_id__icontains=agent)
    if date_from:
        try:
            dtf = datetime.fromisoformat(date_from)
            if timezone.is_naive(dtf):
                dtf = timezone.make_aware(dtf, timezone.get_current_timezone())
            qs = qs.filter(started_at__gte=dtf)
        except Exception:
            pass
    if date_to:
        try:
            dtt = datetime.fromisoformat(date_to)
            if timezone.is_naive(dtt):
                dtt = timezone.make_aware(dtt, timezone.get_current_timezone())
            qs = qs.filter(started_at__lte=dtt)
        except Exception:
            pass

    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'comms/inbox.html', {
        'page_obj': page_obj,
        'q': q,
        'type': comm_type,
        'agent': agent,
        'date_from': date_from,
        'date_to': date_to,
    })


def detail_comm(request, pk: int):
    if not request.user.is_authenticated:
        return render(request, 'account/login.html', status=401)
    obj = get_object_or_404(Communication, pk=pk)
    return render(request, 'comms/detail.html', {'obj': obj})

# Initialize Retell client (API key from env)
_retell_client = None

def get_retell_client():
    global _retell_client
    if _retell_client is None:
        api_key = getattr(settings, 'RETELL_API_KEY', '') or settings.__dict__.get('RETELL_SECRET', '')
        _retell_client = Retell(api_key=api_key)
    return _retell_client

RETELL_BASE_URL = 'https://api.retellai.com'

# Helpers for REST calls

def _http_headers():
    api_key = (
        getattr(settings, 'RETELL_API_KEY', '')
        or getattr(settings, 'RETELL_SECRET', '')
        or getattr(settings, 'RETELL_TOKEN', '')
    )
    return {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

def _rest_chat_create(agent_id, metadata=None, variables=None):
    payload = {
        'agent_id': agent_id,
        'metadata': metadata or {},
        'retell_llm_dynamic_variables': variables or {},
    }
    r = requests.post(f'{RETELL_BASE_URL}/create-chat', headers=_http_headers(), json=payload, timeout=30)
    # Retell returns 201 on success per docs; accept 200-201
    if r.status_code not in (200, 201):
        try:
            err = r.json()
        except Exception:
            err = {'raw': r.text}
        raise Exception(f'create-chat failed: {r.status_code} {err}')
    try:
        return r.json()
    except Exception:
        raise Exception(f'Invalid JSON from create-chat: {r.text[:300]}')

def _rest_chat_send(chat_id, content):
    payload = {
        'chat_id': chat_id,
        'content': content,
    }
    r = requests.post(f'{RETELL_BASE_URL}/create-chat-completion', headers=_http_headers(), json=payload, timeout=60)
    if r.status_code not in (200, 201):
        try:
            err = r.json()
        except Exception:
            err = {'raw': r.text}
        raise Exception(f'create-chat-completion failed: {r.status_code} {err}')
    try:
        return r.json()
    except Exception:
        raise Exception(f'Invalid JSON from create-chat-completion: {r.text[:300]}')

# --- Chat MVP (placeholder until real Web Chat API available) ---
def _extract_chat_id(resp):
    # Support dict responses from REST API
    if isinstance(resp, dict):
        return resp.get('chat_id') or resp.get('id') or resp.get('session_id')
    # SDK object support still here, but REST is primary
    if hasattr(resp, 'chat_id'):
        return getattr(resp, 'chat_id')
    if hasattr(resp, 'id'):
        return getattr(resp, 'id')
    return None

# Try to extract an assistant reply from various response shapes
def _extract_reply(resp):
    # messages list with roles
    messages = None
    if hasattr(resp, 'messages'):
        messages = getattr(resp, 'messages')
    elif isinstance(resp, dict):
        messages = resp.get('messages') or resp.get('output_messages')
    if isinstance(messages, list):
        for m in reversed(messages):
            role = m.get('role') if isinstance(m, dict) else getattr(m, 'role', None)
            if role and str(role).lower() in ('assistant', 'ai', 'agent', 'assistant_role'):
                return m.get('content') if isinstance(m, dict) else getattr(m, 'content', '')
    # choices like OpenAI
    choices = None
    if hasattr(resp, 'choices'):
        choices = getattr(resp, 'choices')
    elif isinstance(resp, dict):
        choices = resp.get('choices')
    if isinstance(choices, list) and choices:
        choice = choices[-1]
        if isinstance(choice, dict):
            msg = choice.get('message')
            if isinstance(msg, dict):
                return msg.get('content') or ''
        content = choice.get('content') if isinstance(choice, dict) else getattr(choice, 'content', None)
        if content:
            return content
    # direct fields
    for key in ('reply', 'text', 'content', 'output_text'):
        if hasattr(resp, key):
            return getattr(resp, key)
        if isinstance(resp, dict) and resp.get(key):
            return resp.get(key)
    return ''

# Wrapper to create chat across potential SDK variants
def _retell_chat_create(client, agent_id, metadata=None, variables=None):
    chat = getattr(client, 'chat', None)
    if chat is None:
        raise Exception('Chat API not available in SDK')
    # Preferred
    if hasattr(chat, 'create'):
        return chat.create(agent_id=agent_id, metadata=metadata or {}, retell_llm_dynamic_variables=variables or {})
    # Possible variant: sessions.create
    sessions = getattr(chat, 'sessions', None)
    if sessions is not None and hasattr(sessions, 'create'):
        return sessions.create(agent_id=agent_id, metadata=metadata or {}, retell_llm_dynamic_variables=variables or {})
    # Fallback: try generic create with only agent_id
    return chat.create(agent_id=agent_id)

# Wrapper to send a message / get completion across variants
def _retell_chat_send(client, chat_id, content):
    chat = getattr(client, 'chat', None)
    if chat is None:
        raise Exception('Chat API not available in SDK')
    # Known pattern
    if hasattr(chat, 'create_completion'):
        return chat.create_completion(chat_id=chat_id, content=content)
    # OpenAI-like nested resource
    completions = getattr(chat, 'completions', None)
    if completions is not None and hasattr(completions, 'create'):
        return completions.create(chat_id=chat_id, content=content)
    # Messages subresource
    messages = getattr(chat, 'messages', None)
    if messages is not None and hasattr(messages, 'create'):
        return messages.create(chat_id=chat_id, content=content)
    # Single-method variant
    if hasattr(chat, 'send_message'):
        return chat.send_message(chat_id=chat_id, content=content)
    # Fallback: try calling create with chat_id + content
    if hasattr(chat, 'create'):
        try:
            return chat.create(chat_id=chat_id, content=content)
        except Exception:
            pass
    raise Exception('No supported chat completion method found in SDK')

def _clean_id(val: str) -> str:
    if not val:
        return ''
    # Strip inline comments and whitespace
    return val.split('#', 1)[0].strip()


def _record_usage_from_resp(comm: Communication, resp: dict):
    if not isinstance(resp, dict) or not comm:
        return
    usage = resp.get('usage') or resp.get('token_usage') or {}
    # Common fields
    in_tokens = usage.get('prompt_tokens') or usage.get('input_tokens') or usage.get('in')
    out_tokens = usage.get('completion_tokens') or usage.get('output_tokens') or usage.get('out')
    total_tokens = usage.get('total_tokens') or usage.get('total')
    # Some providers return flat fields
    in_tokens = in_tokens or resp.get('prompt_tokens') or resp.get('input_tokens')
    out_tokens = out_tokens or resp.get('completion_tokens') or resp.get('output_tokens')
    total_tokens = total_tokens or resp.get('total_tokens')
    changed = False
    if in_tokens is not None:
        comm.tokens_input = int(in_tokens)
        changed = True
    if out_tokens is not None:
        comm.tokens_output = int(out_tokens)
        changed = True
    if total_tokens is not None:
        comm.tokens_total = int(total_tokens)
        changed = True
    if changed:
        comm.save(update_fields=['tokens_input', 'tokens_output', 'tokens_total', 'updated_at'])

@csrf_exempt
def open_web_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'authentication required'}, status=401)
        payload = json.loads(request.body.decode('utf-8') or '{}')
        agent_id = _clean_id(payload.get('agent_id') or getattr(settings, 'RETELL_CHAT_AGENT_ID', '') or getattr(settings, 'RETELL_DEFAULT_AGENT_ID', ''))
        if not agent_id:
            return JsonResponse({'error': 'agent_id required'}, status=400)
        # Use REST API
        resp = _rest_chat_create(
            agent_id=agent_id,
            metadata={'user_id': request.user.id, **(payload.get('metadata') or {})},
            variables=payload.get('variables') or {},
        )
        chat_id = _extract_chat_id(resp)
        if not chat_id:
            return JsonResponse({'error': 'chat_id not returned by provider'}, status=500)
        status = resp.get('chat_status') or resp.get('status') if isinstance(resp, dict) else None
        # Persist record
        started = timezone.now()
        Communication.objects.get_or_create(
            external_id=str(chat_id),
            comm_type=Communication.TYPE_CHAT,
            defaults={
                'user': request.user,
                'agent_id': agent_id,
                'started_at': started,
                'metadata': {'source': 'web', 'status': status},
            },
        )
        return JsonResponse({'chat_id': chat_id, 'status': status})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def send_web_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'authentication required'}, status=401)
        data = json.loads(request.body.decode('utf-8') or '{}')
        chat_id = data.get('chat_id') or data.get('session_id')
        message = data.get('message') or data.get('content')
        if not chat_id:
            # Auto-create chat with REST using provided agent_id
            agent_id = _clean_id(data.get('agent_id') or getattr(settings, 'RETELL_CHAT_AGENT_ID', '') or getattr(settings, 'RETELL_DEFAULT_AGENT_ID', ''))
            if not agent_id:
                return JsonResponse({'error': 'agent_id required to open chat'}, status=400)
            create_resp = _rest_chat_create(agent_id=agent_id, metadata={'user_id': request.user.id})
            chat_id = _extract_chat_id(create_resp)
            if not chat_id:
                return JsonResponse({'error': 'failed to open chat session'}, status=500)
        if not message:
            return JsonResponse({'error': 'message required'}, status=400)
        # Send message via REST
        resp = _rest_chat_send(chat_id=chat_id, content=message)
        reply_text = _extract_reply(resp)
        # Update usage if present
        try:
            comm = Communication.objects.filter(external_id=str(chat_id), comm_type=Communication.TYPE_CHAT).first()
            if comm:
                _record_usage_from_resp(comm, resp if isinstance(resp, dict) else {})
        except Exception:
            pass
        return JsonResponse({'reply': reply_text, 'chat_id': chat_id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def create_web_call(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'authentication required'}, status=401)
        data = json.loads(request.body.decode('utf-8') or '{}')
        agent_id = (data.get('agent_id') or getattr(settings, 'RETELL_DEFAULT_AGENT_ID', '')).strip()
        if not agent_id:
            return JsonResponse({'error': 'agent_id required'}, status=400)
        client = get_retell_client()
        try:
            resp = client.call.create_web_call(
                agent_id=agent_id,
                metadata={'user_id': request.user.id, **(data.get('metadata') or {})},
                retell_llm_dynamic_variables=data.get('variables') or {}
            )
        except Exception as e:
            return JsonResponse({'error': f'create_web_call failed: {e}'}, status=400)
        # Support object or dict
        access_token = getattr(resp, 'access_token', None) if not isinstance(resp, dict) else resp.get('access_token')
        call_id = getattr(resp, 'call_id', None) if not isinstance(resp, dict) else resp.get('call_id')
        # Persist call record
        try:
            Communication.objects.get_or_create(
                external_id=str(call_id or ''),
                comm_type=Communication.TYPE_CALL,
                defaults={
                    'user': request.user,
                    'agent_id': agent_id,
                    'started_at': timezone.now(),
                    'metadata': {'source': 'web', 'status': 'created'},
                }
            )
        except Exception:
            pass
        return JsonResponse({'access_token': access_token, 'call_id': call_id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def _mask(s: str) -> str:
    if not s:
        return ''
    if len(s) <= 6:
        return '*' * len(s)
    return s[:3] + '***' + s[-3:]

@csrf_exempt
def debug(request):
    # Minimal config probe; avoid leaking full secrets; allow only staff/superusers
    if not request.user.is_authenticated or not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'error': 'forbidden'}, status=403)
    api_key = (
        getattr(settings, 'RETELL_API_KEY', '')
        or getattr(settings, 'RETELL_SECRET', '')
        or getattr(settings, 'RETELL_TOKEN', '')
    )
    data = {
        'has_api_key': bool(api_key),
        'api_key_sample': _mask(api_key),
        'default_agent_id': getattr(settings, 'RETELL_DEFAULT_AGENT_ID', ''),
        'chat_agent_id': getattr(settings, 'RETELL_CHAT_AGENT_ID', ''),
    }
    return JsonResponse(data)


"""Webhook logic moved to DRF APIView in views_webhooks.RetellWebhookView"""
