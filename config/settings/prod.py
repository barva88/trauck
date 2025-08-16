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
# Base de datos: usa DATABASE_URL si está definido, si no, fallback a sqlite
# -----------------------------------------------------------------------------
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),  # noqa: F405
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
