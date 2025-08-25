"""
Production settings. Inherits from base and only overrides env-specific parts.
- Static/Media storage is defined per environment via STORAGES.
- WhiteNoise is enabled in prod (inserted after SecurityMiddleware).
"""

from .base import *  # noqa
import os

# Core toggles
DEBUG = False
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else []

# Per-env storages: WhiteNoise for static in production
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "LOCATION": str(MEDIA_ROOT),
        "BASE_URL": MEDIA_URL,
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        "LOCATION": str(STATIC_ROOT),
        "BASE_URL": STATIC_URL,
    },
}

# Ensure WhiteNoise is placed right after SecurityMiddleware
if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# -----------------------------------------------------------------------------
# Security & HTTPS hardening for production
# -----------------------------------------------------------------------------
# Respect reverse proxy SSL headers (Nginx/Gunicorn)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Force HTTPS and enable strong HSTS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Secure cookies and sane SameSite defaults
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = os.getenv("CSRF_COOKIE_SAMESITE", "Lax")

# Optional cookie domains (cross-subdomain auth)
SESSION_COOKIE_DOMAIN = os.getenv("SESSION_COOKIE_DOMAIN", ".trauck.com")
CSRF_COOKIE_DOMAIN = os.getenv("CSRF_COOKIE_DOMAIN", ".trauck.com")

# Additional secure headers via SecurityMiddleware
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = os.getenv("SECURE_REFERRER_POLICY", "strict-origin-when-cross-origin")
X_FRAME_OPTIONS = os.getenv("X_FRAME_OPTIONS", "DENY")

# CSRF trusted origins (comma-separated env var)
_csrf_trusted = os.getenv(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "https://trauck.com,https://www.trauck.com,https://dashboard.trauck.com",
)
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_trusted.split(",") if o.strip()]

# -----------------------------------------------------------------------------
# Email (production): SMTP via environment (Gmail or provider)
# -----------------------------------------------------------------------------
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")  # noqa: F405
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")  # noqa: F405
EMAIL_PORT = env.int("EMAIL_PORT", default=587)  # noqa: F405
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)  # noqa: F405
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")  # noqa: F405
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")  # noqa: F405
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)  # noqa: F405

# -----------------------------------------------------------------------------
# DB: prioridad DATABASE_URL + fallback Supabase (Pooler)
# -----------------------------------------------------------------------------
import os as _os, urllib.parse as _urllib
import dj_database_url as _dj

def _to_bool(v: str, default=False):
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}

_db_url = _os.getenv("DATABASE_URL")
if _db_url:
    DATABASES = {
        "default": _dj.parse(
            _db_url,
            conn_max_age=int(_os.getenv("DB_CONN_MAX_AGE", "600")),
            ssl_require=True,
        )
    }
else:
    use_pooler = _to_bool(_os.getenv("SUPABASE_USE_POOLER", "true"), default=True)
    user = _os.getenv("SUPABASE_DB_USER", "postgres")
    pwd = _os.getenv("SUPABASE_DB_PASSWORD", "")
    dbname = _os.getenv("SUPABASE_DB_NAME", "postgres")
    sslm = _os.getenv("DB_SSLMODE", "require")

    if use_pooler:
        host = _os.getenv("SUPABASE_POOLER_HOST", "")
        port = _os.getenv("SUPABASE_POOLER_PORT", "6543")
    else:
        host = _os.getenv("SUPABASE_DIRECT_HOST", "")
        port = _os.getenv("SUPABASE_DIRECT_PORT", "5432")

    if host and pwd:
        enc_pwd = _urllib.quote_plus(pwd)
        _fallback_url = f"postgresql://{user}:{enc_pwd}@{host}:{port}/{dbname}?sslmode={sslm}"
        DATABASES = {
            "default": _dj.parse(
                _fallback_url,
                conn_max_age=int(_os.getenv("DB_CONN_MAX_AGE", "600")),
                ssl_require=True,
            )
        }

# -----------------------------------------------------------------------------
# CORS (django-cors-headers)
# - Habilita middleware y app; controla orígenes vía variables de entorno
# -----------------------------------------------------------------------------
if "corsheaders" not in INSTALLED_APPS:
    INSTALLED_APPS += ["corsheaders"]
if "corsheaders.middleware.CorsMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(1, "corsheaders.middleware.CorsMiddleware")
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])  # noqa: F405
CORS_ALLOW_ALL_ORIGINS = env.bool("CORS_ALLOW_ALL_ORIGINS", default=False)  # noqa: F405

# -----------------------------------------------------------------------------
# Logging: salida simple a stdout con nivel configurable por entorno
# -----------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"}
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "simple"}},
    "root": {"handlers": ["console"], "level": env("DJANGO_LOG_LEVEL", default="INFO")},  # noqa: F405
}

# -----------------------------------------------------------------------------
# Sentry (opcional): se carga de forma perezosa para evitar dependencia dura
# -----------------------------------------------------------------------------
SENTRY_DSN = env("SENTRY_DSN", default=None)  # noqa: F405
if SENTRY_DSN:
    try:
        import importlib

        sentry_sdk = importlib.import_module("sentry_sdk")
        DjangoIntegration = importlib.import_module("sentry_sdk.integrations.django").DjangoIntegration
        sentry_sdk.init(dsn=SENTRY_DSN, integrations=[DjangoIntegration()])
    except Exception:
        # Si Sentry no está instalado o falla la inicialización, continúa sin romper el arranque
        pass
