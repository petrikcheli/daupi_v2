from .base import *

DEBUG = False

ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "dbname",
        "USER": "dbuser",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
