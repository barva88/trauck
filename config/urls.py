"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.urls import reverse, NoReverseMatch
from django.views.generic import TemplateView
from allauth.account.views import email_verification_sent
from django.views.generic import RedirectView
from rest_framework.authtoken.views import obtain_auth_token # <-- NEW


from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Public landing (default root for now; will be host-mapped later)
    path('', include('apps.public.urls')),
    # Dashboard/pages
    path('', include('apps.pages.urls')),
    path('accounts/', include('apps.accounts.urls')),
    # Allauth (web)
    path('accounts/', include('allauth.urls')),
    # Compatibility: map admin_black demo names to allauth equivalents
    path('auth/signin/', RedirectView.as_view(pattern_name='account_login', permanent=False), name='auth_signin'),
    path('auth/signup/', RedirectView.as_view(pattern_name='account_signup', permanent=False), name='auth_signup'),
    # Compatibility: legacy demo menu names -> home
    path('icons/', RedirectView.as_view(pattern_name='pages:index', permanent=False), name='icons'),
    path('map/', RedirectView.as_view(pattern_name='pages:index', permanent=False), name='map'),
    path('notifications/', RedirectView.as_view(pattern_name='pages:index', permanent=False), name='notifications'),
    path('user-profile/', RedirectView.as_view(pattern_name='pages:index', permanent=False), name='user_profile'),
    path('tables/', RedirectView.as_view(pattern_name='pages:index', permanent=False), name='tables'),
    path('typography/', RedirectView.as_view(pattern_name='pages:index', permanent=False), name='typography'),
    path('rtl/', RedirectView.as_view(pattern_name='pages:index', permanent=False), name='rtl'),
    path('upgrade/', RedirectView.as_view(pattern_name='pages:index', permanent=False), name='upgrade'),
    # dj-rest-auth (API)
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    # Ensure the named view exists for verification sent pages
    path('accounts/email-verification-sent/', email_verification_sent, name='account_email_verification_sent'),

    path('brokers/', include('apps.brokers.urls')),
    path('carriers/', include('apps.carriers.urls')),
    path('core/', include('apps.core.urls')),
    path('dispatch/', include('apps.dispatch.urls')),
    path('documents/', include('apps.documents.urls')),
    path('drivers/', include('apps.drivers.urls')),
    path('loads/', include('apps.loads.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('payments/', include('apps.payments.urls')),
    path('trucks/', include('apps.trucks.urls')),
    path('my_profile/', include('apps.my_profile.urls')),
    path('education/', include('apps.education.urls')),
    path('billing/', include('apps.billing.urls')),
    path('api/education/', include(('apps.education.urls','education'), namespace='education_api')),
    path('', include('apps.dyn_dt.urls')),
    path('', include('apps.dyn_api.urls')),
    path('charts/', include('apps.charts.urls')),
    path("admin/", admin.site.urls),
    path('analytics/', include('apps.analytics.urls')),
    path('comms/', include('apps.comms.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Lazy-load on routing is needed
# During the first build, API is not yet generated
try:
    urlpatterns.append( path("api/"      , include("api.urls"))    )
    urlpatterns.append( path("login/jwt/", view=obtain_auth_token) )
except:
    pass

# Ensure API verification-sent endpoint resolves a template (fallback only if missing)
try:
    reverse('account_email_verification_sent')
except Exception:
    urlpatterns.append(
        path(
            'api/auth/registration/account-email-verification-sent/',
            TemplateView.as_view(template_name='account/verification_sent.html'),
            name='account_email_verification_sent',
        )
    )

# Django Debug Toolbar routing (only when installed and DEBUG is True)
if settings.DEBUG:
    try:
        import debug_toolbar  # type: ignore
        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
    except Exception:
        # If debug toolbar isn't installed, ignore
        pass