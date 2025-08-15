from .base import *  # noqa

DEBUG = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "test.sqlite3"}
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Include production domains for allowed hosts test
ALLOWED_HOSTS = [
    "trauck.com",
    "dashboard.trauck.com",
    "localhost",
    "127.0.0.1",
]
from .base import *  # noqa

DEBUG = False

# Speed up tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
