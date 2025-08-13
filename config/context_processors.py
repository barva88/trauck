from django.conf import settings
from .menu_config import MENU_ITEMS

def feature_flags(request):
    return {
        'STRIPE_UI_PREVIEW': getattr(settings, 'STRIPE_UI_PREVIEW', False),
    }

def retell_settings(request):
    return {
        'RETELL_DEFAULT_AGENT_ID': getattr(settings, 'RETELL_DEFAULT_AGENT_ID', ''),
        'RETELL_CHAT_AGENT_ID': getattr(settings, 'RETELL_CHAT_AGENT_ID', ''),
    }

def sidebar_menu(request):
    # Determine current segment/path to mark active menu entries
    path = request.path or '/'
    # Segment heuristic: first path component
    try:
        segment = path.strip('/').split('/')[0]
    except Exception:
        segment = ''
    return {
        'menu_items': MENU_ITEMS,
        'segment': segment,
    }
