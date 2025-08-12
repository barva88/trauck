from rest_framework.permissions import BasePermission


class IsAuthenticatedAndOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        owner = getattr(obj, 'user', None)
        return owner == request.user
