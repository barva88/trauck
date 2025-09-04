from .base import *  # noqa

# Dev settings inherit from base and keep things simple.
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Per-env storages: no WhiteNoise in development
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "LOCATION": str(MEDIA_ROOT),
        "BASE_URL": MEDIA_URL,
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        "LOCATION": str(STATIC_ROOT),
        "BASE_URL": STATIC_URL,
    },
}

# Ensure WhiteNoise is not active in dev
if "whitenoise.middleware.WhiteNoiseMiddleware" in MIDDLEWARE:
    MIDDLEWARE.remove("whitenoise.middleware.WhiteNoiseMiddleware")

# Email in development: console backend (no actual delivery)
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")  # noqa: F405
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@example.com")  # noqa: F405


# --- Development: force local URLs -----------------------------------------
# When running in the `dev` settings we want all generated URLs to point to
# localhost or use relative paths so the site works without DNS/hosts tweaks.
# Keep PARENT_HOST empty so base.py falls back to relative LOGIN_URL ("/accounts/login/").
PARENT_HOST = ""
# Use plain http scheme in dev
HOST_SCHEME = "http://"
# Ensure Stripe portal return (and similar configured absolute URLs) point to localhost
STRIPE_PORTAL_RETURN_URL = env("STRIPE_PORTAL_RETURN_URL", default="http://localhost:8000/")
# No external render hostname in dev
RENDER_EXTERNAL_HOSTNAME = None

# Force login and account URLs to local / relative paths in development
LOGIN_URL = "/accounts/login/"
# Allauth/email defaults to https in base; use http in dev
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"

