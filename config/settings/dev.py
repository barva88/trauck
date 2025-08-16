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
