from .base import *

DEBUG = False

DATABASES = {
    "default": postgres_database_config()
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
