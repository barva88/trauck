"""
Base settings shared across environments.
"""
from pathlib import Path
import os
import environ
import dj_database_url
import urllib.parse



env = environ.Env(
    DEBUG=(bool, False),
)

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env early using python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except Exception:
    pass

SECRET_KEY = env("SECRET_KEY", default="Super_Secr3t_9999")
DEBUG = env.bool("DJANGO_DEBUG", default=env.bool("DEBUG", default=False))

ALLOWED_HOSTS = ["*"]
RENDER_EXTERNAL_HOSTNAME = env("RENDER_EXTERNAL_HOSTNAME", default=None)
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:5085",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5085",
]

INSTALLED_APPS = [
    "django_hosts",
    "jazzmin",
    "admin_black",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Serve UI pages
    "apps.pages",

    # Dynamic DT
    "apps.dyn_dt",

    # Dynamic API
    "apps.dyn_api",

    # Charts
    "apps.charts",

    # Auth / API
    "rest_framework",
    "rest_framework.authtoken",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "widget_tweaks",

    # My Apps
    "apps.accounts",
    "apps.carriers",
    "apps.brokers",
    "apps.drivers",
    "apps.trucks",
    "apps.loads",
    "apps.dispatch",
    "apps.documents",
    "apps.payments",
    "apps.notifications",
    "apps.core",
    "apps.my_profile",
    "apps.education",
    "apps.billing",
    "apps.analytics",
    "apps.comms",
    "apps.public",
]

AUTH_USER_MODEL = "accounts.User"
SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

MIDDLEWARE = [
    "django_hosts.middleware.HostsRequestMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_hosts.middleware.HostsResponseMiddleware",
    "apps.core.middleware.RequireLoginOnDashboardHost",
]

ROOT_URLCONF = "config.urls_dashboard"  # default for dashboard host
ROOT_HOSTCONF = "config.hosts"
DEFAULT_HOST = env("DEFAULT_HOST", default="dashboard")
PARENT_HOST = env("PARENT_HOST", default="trauck.com")
HOST_SCHEME = env("HOST_SCHEME", default="https://")

HOME_TEMPLATES = os.path.join(BASE_DIR, "templates")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [HOME_TEMPLATES],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.feature_flags",
                "config.context_processors.retell_settings",
                "config.context_processors.sidebar_menu",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# -----------------------------------------------------------------------------
# Database (Supabase)
# Priority to DATABASE_URL; otherwise build from SUPABASE_* variables.
# Default: use Pooler (port 6543), require SSL, and enable connection pooling.
# -----------------------------------------------------------------------------

def _bool(v: str, default: bool = False) -> bool:
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}

DATABASE_URL = os.getenv("DATABASE_URL")

# Development fallback: when running with DEBUG enabled and no DATABASE_URL
# is provided, default to a local sqlite file so developers don't need to set
# Supabase/Postgres vars for normal local work.
# Note: `dev.py` sets DEBUG after importing base, so also consider the
# DJANGO_SETTINGS_MODULE to detect the development settings early.
settings_module = os.getenv("DJANGO_SETTINGS_MODULE", "")
is_dev_settings = "dev" in settings_module.lower()

if not DATABASE_URL and (DEBUG or is_dev_settings):
    # Use BASE_DIR to build an absolute path to db.sqlite3
    DATABASE_URL = f"sqlite:///{str(BASE_DIR / 'db.sqlite3')}"

if not DATABASE_URL:
    use_pooler = _bool(os.getenv("SUPABASE_USE_POOLER", "true"), default=True)
    user = os.getenv("SUPABASE_DB_USER", "postgres")
    pwd = os.getenv("SUPABASE_DB_PASSWORD", "")
    dbname = os.getenv("SUPABASE_DB_NAME", "postgres")
    sslm = os.getenv("DB_SSLMODE", "require")

    if use_pooler:
        host = os.getenv("SUPABASE_POOLER_HOST", "")
        port = os.getenv("SUPABASE_POOLER_PORT", "6543")
    else:
        host = os.getenv("SUPABASE_DIRECT_HOST", "")
        port = os.getenv("SUPABASE_DIRECT_PORT", "5432")

    if not (host and pwd):
        raise RuntimeError(
            "Faltan variables de DB: define DATABASE_URL o SUPABASE_DB_PASSWORD y el host correspondiente."
        )

    enc_pwd = urllib.parse.quote_plus(pwd)
    DATABASE_URL = f"postgresql://{user}:{enc_pwd}@{host}:{port}/{dbname}?sslmode={sslm}"

# Determine whether to require SSL for dj-database-url parsing.
# For sqlite URLs ssl/sslmode options are not applicable and can break the
# connection (sqlite backend doesn't accept sslmode), so disable ssl_require
# when using sqlite.
_ssl_require = True
if DATABASE_URL and DATABASE_URL.startswith("sqlite:"):
    _ssl_require = False

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=int(os.getenv("DB_CONN_MAX_AGE", "600")),
        ssl_require=_ssl_require,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static/Media base paths (used by all environments)
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_ROOT = BASE_DIR / "media"
STATICFILES_DIRS = []
if (BASE_DIR / "static").exists():
    STATICFILES_DIRS.append(BASE_DIR / "static")
if (BASE_DIR / "assets").exists():
    STATICFILES_DIRS.append(BASE_DIR / "assets")
WHITENOISE_USE_FINDERS = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "/"
# Force a host-aware LOGIN_URL so any redirection to login uses the dashboard host
if PARENT_HOST:
    LOGIN_URL = f"{HOST_SCHEME}dashboard.{PARENT_HOST}/accounts/login/"
else:
    LOGIN_URL = "/accounts/login/"
# Email configuration — prefer values from environment (.env).
# Default to SMTP backend so production-like behavior can be tested locally.
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")

# SMTP / Gmail settings (all values come from .env)
# Examples (in .env):
#   EMAIL_HOST=smtp.gmail.com
#   EMAIL_PORT=587
#   EMAIL_HOST_USER=your@gmail.com
#   EMAIL_HOST_PASSWORD=your-app-password
#   EMAIL_USE_TLS=True
#   EMAIL_USE_SSL=False
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env("EMAIL_PORT", default=587)
# EMAIL_HOST_USER / PASSWORD: fall back to GMAIL_* names for convenience
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default=env("GMAIL_USER", default=""))
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default=env("GMAIL_PASSWORD", default=""))
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_USE_SSL = env.bool("EMAIL_USE_SSL", default=False)

# Default from email — use explicit env var or the SMTP user
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default=(EMAIL_HOST_USER or "no-reply@example.com"))

DYNAMIC_DATATB = {
    "product": "apps.pages.models.Product",
}

DYNAMIC_API = {
    "product": "apps.pages.models.Product",
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}
REST_USE_JWT = True
SIMPLE_JWT = {"AUTH_HEADER_TYPES": ("Bearer",)}

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Trauck] "
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"
ACCOUNT_RATE_LIMITS = {"login_failed": "5/5m"}
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"
ACCOUNT_ADAPTER = "apps.accounts.adapters.AccountAdapter"
ACCOUNT_FORMS = {"signup": "apps.accounts.forms.CustomSignupForm"}
LOGIN_REDIRECT_URL = "/"  # within dashboard host
LOGOUT_REDIRECT_URL = "/"

# Host-aware URLs for allauth/dj-rest-auth (used by emails or external redirects)
ACCOUNT_ADAPTER = "apps.accounts.adapters.AccountAdapter"

RETELL_WEBHOOK_SECRET = env("RETELL_WEBHOOK_SECRET", default="changeme")
RETELL_ALLOWED_AGENT_IDS = env("RETELL_ALLOWED_AGENT_IDS", default="")

RETELL_API_KEY = env("RETELL_API_KEY", default=env("RETELL_TOKEN", default=""))
RETELL_DEFAULT_AGENT_ID = env("RETELL_DEFAULT_AGENT_ID", default=env("RETELL_AGENT_ID", default=""))
RETELL_CHAT_AGENT_ID = env("RETELL_CHAT_AGENT_ID", default=env("RETELL_AGENT_CHAT_ID", default=""))

STRIPE_SECRET_KEY = env("STRIPE_SECRET_KEY", default="")
STRIPE_PUBLISHABLE_KEY = env("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_WEBHOOK_SECRET = env("STRIPE_WEBHOOK_SECRET", default="")
STRIPE_PORTAL_RETURN_URL = env("STRIPE_PORTAL_RETURN_URL", default="http://localhost:8000/")
STRIPE_PORTAL_CONFIGURATION_ID = env("STRIPE_PORTAL_CONFIGURATION_ID", default="")

BILLING_REFUND_PRO_RATA = env.bool("BILLING_REFUND_PRO_RATA", default=False)
BILLING_DEFAULT_EXAM_COST_CREDITS = env.int("BILLING_DEFAULT_EXAM_COST_CREDITS", default=1)
BILLING_ALLOW_REFUND_IF_USED_THRESHOLD = env.int("BILLING_ALLOW_REFUND_IF_USED_THRESHOLD", default=0)
BILLING_CREDIT_CARRYOVER = env.bool("BILLING_CREDIT_CARRYOVER", default=False)

STRIPE_UI_PREVIEW = env.bool("STRIPE_UI_PREVIEW", default=False)

EDU_PASS_THRESHOLD = env.float("EDU_PASS_THRESHOLD", default=70.0)
EDU_REVEAL_CORRECT_ANSWERS = env.bool("EDU_REVEAL_CORRECT_ANSWERS", default=False)
EDU_EXPIRE_MINUTES = env.int("EDU_EXPIRE_MINUTES", default=120)
