from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django_hosts.resolvers import reverse


class RequireLoginOnDashboardHost(MiddlewareMixin):
    def process_request(self, request):
        host = request.get_host().split(':')[0]
        dashboard_host = f"dashboard.{getattr(settings, 'PARENT_HOST', '')}" if getattr(settings, 'PARENT_HOST', None) else None
        if dashboard_host and host == dashboard_host:
            if request.user.is_anonymous:
                # Avoid loops: if already on login URL, do nothing
                try:
                    login_url = reverse('account_login', host='dashboard')
                except Exception:
                    login_url = '/accounts/login/'
                if not request.path.startswith(login_url):
                    return redirect(login_url)
        return None
