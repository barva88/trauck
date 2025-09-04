from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django_hosts.resolvers import reverse


class RequireLoginOnDashboardHost(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().split(':')[0]
        parent = getattr(settings, 'PARENT_HOST', None) or ''
        # If PARENT_HOST is empty (dev) don't prefix with a dot. In dev we allow
        # localhost and 127.0.0.1 to be treated as dashboard host for convenience.
        dashboard_host = f"dashboard.{parent}" if parent else None
        is_dashboard_host = False
        if dashboard_host and host == dashboard_host:
            is_dashboard_host = True
        elif not dashboard_host and host in ("localhost", "127.0.0.1"):
            is_dashboard_host = True
        if is_dashboard_host:
            if request.user.is_anonymous:
                # Allow anonymous access to auth-related endpoints on dashboard host
                allowed_prefixes = (
                    '/accounts/login',
                    '/accounts/signup',
                    '/accounts/confirm-email',
                    '/accounts/password',  # reset/change
                    '/api/auth/',          # dj-rest-auth
                    '/admin/',             # let admin handle its own perms
                )
                for p in allowed_prefixes:
                    if request.path.startswith(p):
                        return None
                # Otherwise redirect to dashboard login URL
                # In production we generate a host-aware URL (dashboard.<PARENT_HOST>).
                # In development (PARENT_HOST empty) return a relative path so the
                # redirect stays on localhost.
                if getattr(settings, 'PARENT_HOST', None):
                    try:
                        login_url = reverse('account_login', host='dashboard')
                    except Exception:
                        login_url = f"{getattr(settings,'HOST_SCHEME','http://')}dashboard.{getattr(settings,'PARENT_HOST')}" + '/accounts/login/'
                else:
                    login_url = '/accounts/login/'
                if not request.path.startswith(login_url):
                    return redirect(login_url)
        return None
