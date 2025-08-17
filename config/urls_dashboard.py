from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required

# Wrap pages index behind login as a simple gate
# Note: apps.pages.urls already applies views; if more locking is needed,
# we can enforce login inside those views or via middleware.

urlpatterns = [
    # Dashboard/pages
    path('', include('apps.pages.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),

    # Compatibility shortcuts
    path('auth/signin/', RedirectView.as_view(pattern_name='account_login', permanent=False), name='auth_signin'),
    path('auth/signup/', RedirectView.as_view(pattern_name='account_signup', permanent=False), name='auth_signup'),

    # dj-rest-auth (API)
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    # App urls
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
    path('analytics/', include('apps.analytics.urls')),
    path('comms/', include('apps.comms.urls')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

try:
    urlpatterns.append(path('api/', include('api.urls')))
except Exception:
    pass
