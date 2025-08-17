from django.urls import include, path

urlpatterns = [
    path('', include('apps.public.urls')),
]
