"""
Base settings shared across environments.
"""
from pathlib import Path
import os
import environ


env = environ.Env(
    DEBUG=(bool, False),
)

# Load .env if present
try:
    environ.Env.read_env(env_file=str(Path(__file__).resolve().parents[2] / ".env"))
except Exception:
    # Fallback to CWD if running ad-hoc scripts
    environ.Env.read_env(env_file=os.path.join(os.getcwd(), ".env"))

# Point to project root (one level above config/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = env("SECRET_KEY", default="Super_Secr3t_9999")
DEBUG = env.bool("DEBUG", default=False)

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


# Database
DB_ENGINE = env("DB_ENGINE", default=None)
DB_USERNAME = env("DB_USERNAME", default=None)
DB_PASS = env("DB_PASS", default=None)
DB_HOST = env("DB_HOST", default=None)
DB_PORT = env("DB_PORT", default=None)
DB_NAME = env("DB_NAME", default=None)

if DB_ENGINE and DB_NAME and DB_USERNAME:
    DATABASES = {
        "default": {
            "ENGINE": f"django.db.backends.{DB_ENGINE}",
            "NAME": DB_NAME,
            "USER": DB_USERNAME,
            "PASSWORD": DB_PASS,
            "HOST": DB_HOST,
            "PORT": DB_PORT,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
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
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="no-reply@example.com")

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
