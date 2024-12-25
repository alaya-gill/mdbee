from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# ----------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="c2TalbtM9VjbTLN5jPsC7pWV3ctlBFy6Jzef4vod7p5MtIRoB3seuRk7vdedJqB7",
)
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
#         "LOCATION": "",
#     }
# }

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Mimicing memcache behavior.
            # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
# EMAIL_HOST = env("EMAIL_HOST", default="smtp.mailgun.org")
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
# EMAIL_PORT = 587
# DEFAULT_FROM_EMAIL='postmaster@sandbox5dd83abbfb59414695022fb38b1fdbc5.mailgun.org'
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.mailgun.org'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'postmaster@sandbox5dd83abbfb59414695022fb38b1fdbc5.mailgun.org'
# EMAIL_HOST_PASSWORD = '8738ddf3e4770fe67c0f8155f104e0ef-6f4beb0a-e8cc053f'
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL='intelligent.nido.1@gmail.com'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'intelligent.nido.1@gmail.com'
EMAIL_HOST_PASSWORD = 'bscn elfp vnlm wggy '




# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ["debug_toolbar"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
if env.str("USE_DOCKER", "no") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [ip[:-1] + "1" for ip in ips]

# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ["django_extensions",'corsheaders',]  # noqa F405
# Celery
# ------------------------------------------------------------------------------

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates
CELERY_TASK_EAGER_PROPAGATES = True
# Your stuff...
# ------------------------------------------------------------------------------
REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = (
    'mdbee.utils.permissions.IsAuthenticatedOrDebugging',
)

# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR("media"))
# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = "/media/"

# # SESSION_COOKIE_DOMAIN = "http://localhost:4200"
# CORS_ALLOW_CREDENTIALS = True
# SESSION_COOKIE_SAMESITE = None

# SESSION_ENGINE="django.contrib.sessions.backends.cache"
S3_ENVIRON = 'local'
# Allow cookies in cross-origin requests
SESSION_COOKIE_SAMESITE = None  # Allow cookies to be sent across origins
CSRF_COOKIE_SAMESITE = None

# Use secure cookies in production (HTTPS)
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
CSRF_COOKIE_SECURE = False     # Set to True in production with HTTPS

# Ensure your frontend's origin is allowed
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Your Vite frontend URL
    "http://127.0.0.1:5173",  # Alternate localhost address if used
]
DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage'
