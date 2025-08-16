"""
Settings de Producción (Nginx + Gunicorn)

Importa base.py y aplica reforzamientos de seguridad con valores por entorno.
Mantiene funcionalidades existentes (WhiteNoise, CORS, logging y Sentry opcional).
"""

from .base import *  # noqa
import os

# -----------------------------------------------------------------------------
# Núcleo: DEBUG y SECRET_KEY
# - DEBUG se controla por la variable DJANGO_DEBUG (default: False)
# - SECRET_KEY se toma de entorno (mismo nombre que en base)
# -----------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=False)  # noqa: F405
SECRET_KEY = env("SECRET_KEY")  # noqa: F405

# -----------------------------------------------------------------------------
# Hosts y CSRF Trusted Origins
# - ALLOWED_HOSTS usa DJANGO_ALLOWED_HOSTS si existe; si no, fija dominios de trauck
# - CSRF_TRUSTED_ORIGINS usa DJANGO_CSRF_TRUSTED_ORIGINS si existe; si no, los https de trauck
# -----------------------------------------------------------------------------
_DEFAULT_ALLOWED = ["trauck.com", "www.trauck.com", "dashboard.trauck.com"]
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=_DEFAULT_ALLOWED)  # noqa: F405

_DEFAULT_TRUSTED = [
    "https://trauck.com",
    "https://www.trauck.com",
    "https://dashboard.trauck.com",
]
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=_DEFAULT_TRUSTED)  # noqa: F405

# -----------------------------------------------------------------------------
# Seguridad de proxy y cookies para uso detrás de Nginx/Load Balancer
# - Forza detección de HTTPS vía cabecera X-Forwarded-Proto y host proxificado
# - Cookies marcadas como Secure y scope de dominio *.trauck.com
# - Redirección a HTTPS + HSTS estricto de 1 año (incluye subdominios, preload)
# - Cabeceras de protección adicionales
# -----------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_DOMAIN = ".trauck.com"
CSRF_COOKIE_DOMAIN = ".trauck.com"
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# -----------------------------------------------------------------------------
# Archivos estáticos (WhiteNoise) y Middleware
# - Inserta WhiteNoise en producción para servir estáticos comprimidos con hash
# - Mantiene STATICFILES_STORAGE y STORAGES para compatibilidad
# -----------------------------------------------------------------------------
if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

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
