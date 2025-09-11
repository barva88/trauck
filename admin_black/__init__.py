# Minimal shim package to satisfy import for `admin_black` used in INSTALLED_APPS
# This provides an empty package so Django can import it during app registry.

__all__ = ["__version__"]
__version__ = "0.0.0"
