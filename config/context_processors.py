from django.conf import settings

def feature_flags(request):
    return {
        'STRIPE_UI_PREVIEW': getattr(settings, 'STRIPE_UI_PREVIEW', False),
    }

def retell_settings(request):
    return {
        'RETELL_DEFAULT_AGENT_ID': getattr(settings, 'RETELL_DEFAULT_AGENT_ID', ''),
        'RETELL_CHAT_AGENT_ID': getattr(settings, 'RETELL_CHAT_AGENT_ID', ''),
    }
