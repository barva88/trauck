"""
Production settings for Nginx + Gunicorn deploys.
Environment-driven, secure by default. DEBUG must be False.
"""
from .base import *  # noqa
import os
from urllib.parse import urlparse

# Core
DEBUG = False
# Use same env var name as base for consistency
SECRET_KEY = env("SECRET_KEY")  # noqa: F405

# Hosts & security
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["*"])  # e.g. ["example.com", "api.example.com"]
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# SSL/Proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 30)  # 30 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Static files handled by WhiteNoise in Gunicorn container or nginx in front
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Database: prefer DATABASE_URL, fallback to sqlite
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),  # noqa: F405
}

# CORS/CSRF
INSTALLED_APPS += ["corsheaders"]
MIDDLEWARE.insert(1, "corsheaders.middleware.CorsMiddleware")
CACHES = CACHES  # noqa: F405 keep whatever is defined in base

# WhiteNoise middleware for static files in prod
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=False)

# Logging (concise JSON-ish to stdout)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s %(levelname)s %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {"handlers": ["console"], "level": env("DJANGO_LOG_LEVEL", default="INFO")},
}

# Optional Sentry (lazy import to avoid hard dependency)
SENTRY_DSN = env("SENTRY_DSN", default=None)
if SENTRY_DSN:
    try:
        import importlib

        sentry_sdk = importlib.import_module("sentry_sdk")
        DjangoIntegration = importlib.import_module("sentry_sdk.integrations.django").DjangoIntegration
        sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()])
    except Exception:
        pass
from .base import *  # noqa

DEBUG = False

# Security hardening (can be tuned in future pass)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Whitenoise static files in production
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
"""
// Generated/updated by Copilot Hardening Task – 2025-08-14
Production settings overlay.
Use DJANGO_SETTINGS_MODULE=config.settings.prod in production.
"""
from .. import settings as base  # type: ignore
import os

for name in dir(base):
    if name.isupper():
        globals()[name] = getattr(base, name)

DEBUG = False
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',') if os.getenv('ALLOWED_HOSTS') else []
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if os.getenv('CSRF_TRUSTED_ORIGINS') else []

SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('1','true','yes')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# TODO: add django-csp, sentry, structured logging in follow-ups
