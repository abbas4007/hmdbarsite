import os
from pathlib import Path
from decouple import config, Csv
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse

BASE_DIR = Path(__file__).resolve().parent.parent

def get_env_variable(var_name, default=None):
    try:
        return config(var_name, default=default)
    except Exception:
        raise ImproperlyConfigured(f"Set the {var_name} environment variable")

# === GENERAL SETTINGS ===
SECRET_KEY = get_env_variable("SECRET_KEY")
DEBUG = config('DEBUG', cast=bool, default=False)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv(), default='127.0.0.1,localhost')

# === APPLICATIONS ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',
    'home',
    'account',
    'captcha',
    # 'csp',
    'django.contrib.humanize',
    "crispy_forms",
    "crispy_bootstrap5",
    'taggit',
    'django_ckeditor_5',
    'ckeditor_uploader',
    'django_jalali',

]
# تنظیمات پایه CKEditor


# مسیر آپلود فایل‌ها (اگر از ckeditor_uploader استفاده می‌کنید)
CKEDITOR_UPLOAD_PATH = "uploads/"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"  # یا 'bootstrap5'
CRISPY_TEMPLATE_PACK = "bootstrap5"
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'djangohmdbar.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'account.context_processors.comisions',

            ],
        },
    },
]

WSGI_APPLICATION = 'djangohmdbar.wsgi.application'

# === DATABASE ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env_variable('DB_NAME'),
        'USER': get_env_variable('DB_USER'),
        'PASSWORD': get_env_variable('DB_PASSWORD'),
        'HOST': get_env_variable('DB_HOST'),
        'PORT': get_env_variable('DB_PORT'),
    }
}

# === PASSWORD VALIDATION ===
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
]

# === INTERNATIONALIZATION ===
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

# === STATIC & MEDIA FILES ===
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / "static"]

# Storage config (S3 / Arvan / Liara)
# USE_S3 = config("USE_S3", cast=bool, default=True)

# if USE_S3:
#     DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
#     AWS_ACCESS_KEY_ID = get_env_variable("AWS_ACCESS_KEY_ID")
#     AWS_SECRET_ACCESS_KEY = get_env_variable("AWS_SECRET_ACCESS_KEY")
#     AWS_STORAGE_BUCKET_NAME = get_env_variable("AWS_STORAGE_BUCKET_NAME")
#     AWS_S3_ENDPOINT_URL = get_env_variable("AWS_S3_ENDPOINT_URL")
#     AWS_S3_FILE_OVERWRITE = False
#     AWS_DEFAULT_ACL = None
#     AWS_QUERYSTRING_AUTH = False
#     MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/"
# else:
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# === AUTH ===
LOGIN_URL = 'account:login'
LOGIN_REDIRECT_URL = 'account:home'

# === SMS API (Ghasedak) ===
GHASEDAK_API_KEY = get_env_variable("GHASEDAK_API_KEY", default="")
SMS_LINE_NUMBER = get_env_variable("SMS_LINE_NUMBER", default="")

# === DEFAULT PRIMARY KEY FIELD ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'account.User'

# X_FRAME_OPTIONS = 'DENY'
# SECURE_CONTENT_TYPE_NOSNIFF = True
# SECURE_BROWSER_XSS_FILTER = True



CONTENT_SECURITY_POLICY = {
'script-src': (
    "'self'",
    'cdn.jsdelivr.net',
    'ajax.googleapis.com',
    'code.jquery.com',
),

    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': (
            "'self'",
            'cdn.jsdelivr.net',
            'ajax.googleapis.com',
            'code.jquery.com',
        ),
        'style-src': (
            "'self'",
            "'unsafe-inline'",
            'cdn.jsdelivr.net',
            'fonts.googleapis.com',
            'use.fontawesome.com',      # ✅ اضافه شد
            'cdn.fontcdn.ir',           # ✅ اضافه شد
        ),
        'font-src': (
            "'self'",
            'fonts.gstatic.com',
            'cdn.fontcdn.ir',
            'cdn.jsdelivr.net',
            'use.fontawesome.com',      # ✅ برای فونت‌های آیکنی
        ),
        'img-src': (
            "'self'",
            'data:',
            'Trustseal.eNamad.ir',
            'trustseal.enamad.ir',
            'cdn.jsdelivr.net',
            'django-shop-center.s3.ir-thr-at1.arvanstorage.ir',  # ✅ اضافه شد
        ),
        'connect-src': ("'self'",),
        'frame-src': (
            "'self'",
            'www.google.com',
            'trustseal.enamad.ir',
        ),
    }
}

# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
# # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True



PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # بهترین گزینه
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'link', 'underline', 'strikethrough', '|',
            'bulletedList', 'numberedList', 'blockQuote', '|',
            'imageUpload', 'mediaEmbed', '|',
            'undo', 'redo'
        ],
        'language': 'fa',  # فارسی‌سازی ادیتور
        'height': '300px',
        'width': '100%',
    },
    'extends': {
        'language': 'fa',
        'blockToolbar': [
            'paragraph', 'heading1', 'heading2', 'heading3', '|',
            'bulletedList', 'numberedList', '|',
            'blockQuote', 'imageUpload'
        ],
        'toolbar': [
            'heading', '|',
            'alignment', '|',
            'fontSize', 'fontFamily', 'fontColor', 'fontBackgroundColor', '|',
            'bold', 'italic', 'underline', 'strikethrough', '|',
            'link', 'imageUpload', 'mediaEmbed', '|',
            'undo', 'redo'
        ],
        'image': {
            'toolbar': ['imageTextAlternative', '|', 'imageStyle:alignLeft', 'imageStyle:full', 'imageStyle:alignRight'],
            'styles': ['full', 'alignLeft', 'alignRight']
        }
    }
}