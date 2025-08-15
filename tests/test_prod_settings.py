import importlib
import os


def test_prod_settings_basic(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    settings = importlib.import_module("config.settings.prod")
    assert settings.DEBUG is False
    assert settings.SECRET_KEY == "test-secret"
    # WhiteNoise storage
    assert settings.STATICFILES_STORAGE.endswith("CompressedManifestStaticFilesStorage")
    # Logging configured
    assert "handlers" in settings.LOGGING
