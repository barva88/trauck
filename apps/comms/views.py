from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from retell import Retell
import json
import requests

# Existing inbox placeholder
@login_required
def inbox(request):
    return HttpResponse('Comms Inbox (MVP placeholder)')

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
    api_key = getattr(settings, 'RETELL_API_KEY', '')
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
        raise Exception(f'create-chat failed: {r.status_code} {r.text}')
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
        raise Exception(f'create-chat-completion failed: {r.status_code} {r.text}')
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

@csrf_exempt
@login_required
def open_web_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
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
        return JsonResponse({'chat_id': chat_id, 'status': status})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
def send_web_chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
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
        return JsonResponse({'reply': reply_text, 'chat_id': chat_id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@login_required
def create_web_call(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
        agent_id = (data.get('agent_id') or getattr(settings, 'RETELL_DEFAULT_AGENT_ID', '')).strip()
        if not agent_id:
            return JsonResponse({'error': 'agent_id required'}, status=400)
        client = get_retell_client()
        resp = client.call.create_web_call(
            agent_id=agent_id,
            metadata={'user_id': request.user.id, **(data.get('metadata') or {})},
            retell_llm_dynamic_variables=data.get('variables') or {}
        )
        # Support object or dict
        access_token = getattr(resp, 'access_token', None) if not isinstance(resp, dict) else resp.get('access_token')
        call_id = getattr(resp, 'call_id', None) if not isinstance(resp, dict) else resp.get('call_id')
        return JsonResponse({'access_token': access_token, 'call_id': call_id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
