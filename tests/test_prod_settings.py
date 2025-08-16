import importlib
import os


def test_prod_settings_basic(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    # Ensure module import reflects env set above
    if "config.settings.prod" in list(importlib.sys.modules.keys()):
        importlib.reload(importlib.import_module("config.settings.prod"))
    settings = importlib.import_module("config.settings.prod")
    assert settings.DEBUG is False
    assert settings.SECRET_KEY == "test-secret"
    # WhiteNoise static storage is configured via STORAGES in prod
    static_backend = settings.STORAGES["staticfiles"]["BACKEND"]
    assert static_backend.endswith("whitenoise.storage.CompressedManifestStaticFilesStorage")
    # Logging configured
    assert "handlers" in settings.LOGGING
