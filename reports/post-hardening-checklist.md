# Post Hardening Checklist

- Versions
  - Python: 3.11+
  - Django: see requirements.txt
  - gunicorn/whitenoise: see requirements.txt
- manage.py check --deploy: (paste output here)
- CI green: (attach screenshot or run link)
- Coverage report generated: coverage.xml
- Env vars used in prod (no values):
  - SECRET_KEY, DJANGO_ALLOWED_HOSTS, DJANGO_CSRF_TRUSTED_ORIGINS
  - DATABASE_URL
  - DJANGO_SECURE_* flags
  - CORS_ALLOWED_ORIGINS / CORS_ALLOW_ALL_ORIGINS
  - EMAIL_BACKEND, DEFAULT_FROM_EMAIL
  - STRIPE_* (optional)
  - SENTRY_DSN (optional)
