import os
import sys
from pathlib import Path

import pymysql

pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.__version__ = "2.2.1"
pymysql.install_as_MySQLdb()

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from labora_shared.env_config import (
    load_dotenv_for_service,
    get_jwt_public_key_path,
    get_db_config,
    mysql_databases,
    read_public_key_pem,
)

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv_for_service(BASE_DIR)

_cfg = get_db_config()
DB_HOST = _cfg["DB_HOST"]
DB_NAME = _cfg["DB_NAME"]
DB_USER = _cfg["DB_USER"]
DB_PASSWORD = _cfg["DB_PASSWORD"]
DB_PORT = _cfg["DB_PORT"]

JWT_PUBLIC_KEY_PATH = get_jwt_public_key_path(BASE_DIR)

# ================================
# DJANGO SECRET & DEBUG
# ================================
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me-job")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = ["*"]


# ================================
# Installed Apps
# ================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "job",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
]

# ================================
# Middleware
# ================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

DATABASES = mysql_databases()


# ================================
# PASSWORD VALIDATION
# ================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ================================
# LANGUAGE & TIME
# ================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ================================
# STATIC
# ================================
STATIC_URL = "static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ================================
# CORS
# ================================
CORS_ALLOW_ALL_ORIGINS = True


# ================================
# JWT CONFIG
# ================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "job.authentication.CustomJWTAuthentication",
    ),
}
JWT_PUBLIC_KEY = read_public_key_pem(JWT_PUBLIC_KEY_PATH)
PUBLIC_KEY = JWT_PUBLIC_KEY

SIMPLE_JWT = {
    "ALGORITHM": "RS256",
    "VERIFYING_KEY": JWT_PUBLIC_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
