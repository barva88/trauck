# Operations Guide

## Environments
- Local: DJANGO_SETTINGS_MODULE=config.settings.dev
- Tests: DJANGO_SETTINGS_MODULE=config.settings.test (already set in pytest.ini)
- Production: DJANGO_SETTINGS_MODULE=config.settings.prod

## Health endpoints
- GET /healthz/ → 200 OK when app is up
- GET /readiness/ → 200 OK if DB reachable, 503 otherwise

## Environment variables
See .env.example. At minimum set:
- SECRET_KEY
- DJANGO_ALLOWED_HOSTS
- DJANGO_CSRF_TRUSTED_ORIGINS
- DATABASE_URL (or use sqlite fallback)

## Staticfiles
- Run collectstatic before deploy
- WhiteNoise CompressedManifest storage is enabled in prod

## Security
- SSL redirect and HSTS enabled by default in prod
- Cookies secure, X-Frame-Options DENY

## CORS/CSRF
- Configure CORS_ALLOWED_ORIGINS and DJANGO_CSRF_TRUSTED_ORIGINS as needed

## Logging
- Logs to stdout with timestamps; adjust DJANGO_LOG_LEVEL if needed

## Optional
- Sentry: set SENTRY_DSN
