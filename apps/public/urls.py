from django.urls import path
from django.views.generic import TemplateView
from .views import HomeView

app_name = "public"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("privacy/", TemplateView.as_view(template_name="public/privacy.html"), name="privacy"),
    path("terms/", TemplateView.as_view(template_name="public/terms.html"), name="terms"),
    path("contact/", TemplateView.as_view(template_name="public/contact.html"), name="contact"),
]
