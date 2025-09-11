"""Compatibility alias: `config.settings.production` imports the real `prod` settings.

Some deployments or environment variables may use `config.settings.production`.
The project uses `prod.py` for production settings; this module re-exports it.
"""

from .prod import *  # noqa: F401,F403
