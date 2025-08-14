from .base import *  # noqa

DEBUG = True

# Enable Django Debug Toolbar if installed
INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE.insert(2, "debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = [
    "127.0.0.1",
]
"""
// Generated/updated by Copilot Hardening Task – 2025-08-14
Development settings extending the current base (config.settings).
Rationale: keep compatibility while introducing per-env overlays.
"""
from .. import settings as base  # type: ignore

# Re-export everything from current settings
for name in dir(base):
    if name.isupper():
        globals()[name] = getattr(base, name)

# Dev toggles
DEBUG = True
ALLOWED_HOSTS = ["*"]
INTERNAL_IPS = ["127.0.0.1", "localhost"]
