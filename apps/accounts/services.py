from allauth.account.models import EmailAddress

def is_email_verified(user):
    if not user or not user.is_authenticated:
        return False
    try:
        return EmailAddress.objects.filter(user=user, verified=True).exists()
    except Exception:
        return False
