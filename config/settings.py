"""
Compatibility wrapper. Import environment-specific settings.
Defaults to dev. Set DJANGO_SETTINGS_MODULE to config.settings.prod for production.
"""

from .settings.dev import *  # noqa: F401,F403

