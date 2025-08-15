from .base import *  # noqa
import os

DEBUG = True
ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ["127.0.0.1", "localhost"]

# SQLite by default for local development
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
}

# Optional: Debug Toolbar if installed
try:
    import debug_toolbar  # noqa: F401
    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(2, "debug_toolbar.middleware.DebugToolbarMiddleware")
except Exception:
    pass
