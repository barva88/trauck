from rest_framework.permissions import BasePermission
from allauth.account.models import EmailAddress

class HasVerifiedEmail(BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        if not EmailAddress.objects.filter(user=user, verified=True).exists():
            return False
        return True
