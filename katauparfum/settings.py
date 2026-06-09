from pathlib import Path
import os
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='django-insecure-@&oow3t&6&@+j0y)5i!(@xg_qsy7@0l=ncp@z)r7%=d5bjpy!1')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = ['*']

RENDER_EXTERNAL_HOSTNAME = env('RENDER_EXTERNAL_HOSTNAME', default=None)
if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS = [f'https://{RENDER_EXTERNAL_HOSTNAME}']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'cloudinary_storage',
    'cloudinary',
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'katauparfum.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.csrf',
                'django.template.context_processors.static',
                'shop.context_processors.currency',
                'shop.context_processors.whatsapp_config',
            ],
        },
    },
]

WSGI_APPLICATION = 'katauparfum.wsgi.application'

DATABASES = {
    'default': env.db('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

WHITENOISE_MANIFEST_STRICT = False

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': env('CLOUDINARY_API_KEY', default=''),
    'API_SECRET': env('CLOUDINARY_API_SECRET', default=''),
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 2592000
SESSION_COOKIE_HTTPONLY = True
SECURE_SSL_REDIRECT = False

WHATSAPP_ADMIN_PHONE = '+22896084619'

JAZZMIN_SETTINGS = {
    "site_title": "KAT AU PARFUM",
    "site_header": "💎 KAT AU PARFUM - Admin",
    "site_brand": "KAT AU PARFUM",
    "welcome_sign": "Bienvenue à l'Administration Luxe KAT AU PARFUM 💎",
    "site_logo": "img/logo.png",
    "site_logo_classes": "img-fluid",
    "site_icon": "img/favicon.png",
    "theme": "default",
    "user_avatar": None,
    "show_sidebar": True,
    "navigation_expanded": True,
    "order_with_respect_to": ["shop", "auth"],
    "show_search": True,
    "search_model_preview": True,
    "responsive_admin": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "shop.category": "fas fa-tags",
        "shop.product": "fas fa-gem",
        "shop.order": "fas fa-shopping-bag",
        "shop.orderitem": "fas fa-cart-plus",
    },
    "default_icon_parents": "fas fa-chevron-right",
    "default_icon_children": "fas fa-arrow-right",
    "useable_permissions": ["auth.add_user", "auth.change_user", "auth.delete_user"],
    "hide_apps": [],
    "show_ui_builder": False,
    "custom_css": "css/jazzmin_custom.css",
    "custom_js": "js/custom_admin.js",
    "related_modal_active": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small": False,
    "footer_small": False,
    "body_small": False,
    "sign_in_maximize": False,
    "windows_overlapped_behavior": True,
    "navbar_fixed": True,
    "presized_sidebar_menu": False,
    "navbar_color": "#1a1a1a",
    "navbar_text_color": "#d4af37",
    "navbar_small_text": True,
    "navbar_variant": "dark",
    "body_bg": "linear-gradient(135deg, #faf8f3 0%, #f4ede4 100%)",
    "sidebar_bg": "linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%)",
    "sidebar_text_color": "#d4af37",
    "sidebar_nav_small_text": True,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_fixed": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
}