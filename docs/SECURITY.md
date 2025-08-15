# Security

- SecurityMiddleware first in MIDDLEWARE
- HTTPS enforced (SECURE_SSL_REDIRECT) in prod
- HSTS enabled with subdomains and preload in prod
- Cookies Secure and CSRF cookie secure in prod
- CSRF trusted origins configured via env
- ALLOWED_HOSTS must include trauck.com and dashboard.trauck.com
- Optional Sentry: set SENTRY_DSN
- Keep dependencies updated; bandit runs in CI
