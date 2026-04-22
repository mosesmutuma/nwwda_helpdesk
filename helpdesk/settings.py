import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-nwwda-custom-key-!@#$%^&*(123456789)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# --- NECESSARY FOR DEPLOYMENT ---
ALLOWED_HOSTS = ['*']

# --- DYNAMIC URL SETTING FOR EMAIL LINKS ---
if os.environ.get('RENDER'):
    SITE_URL = 'https://nwwda-helpdesk.onrender.com'
else:
    SITE_URL = 'http://127.0.0.1:8000'

# Application definition
INSTALLED_APPS = [
    'jazzmin',  # Must be before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tickets',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Necessary for Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'helpdesk.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'tickets' / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tickets.context_processors.ticket_stats', 
            ],
        },
    },
]

WSGI_APPLICATION = 'helpdesk.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# --- AUTHENTICATION REDIRECTS ---
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
REDIRECT_FIELD_NAME = 'next'

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "tickets" / "static"]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Necessary for Render

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- EMAIL CONFIGURATION (Gmail SMTP) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'nwwdaict@gmail.com'
# UPDATED: Using the new App Password provided
EMAIL_HOST_PASSWORD = 'ljls ttcz lucu xocs'
DEFAULT_FROM_EMAIL = 'NWWDA ICT Helpdesk <nwwdaict@gmail.com>'

# --- JAZZMIN ADMIN SETTINGS ---
JAZZMIN_SETTINGS = {
    "site_title": "NWWDA ICT Admin",
    "site_header": "NWWDA",
    "site_brand": "NWWDA ICT",
    "site_logo": "images/logo.jpg",
    "login_logo": "images/logo.jpg",
    "copyright": "Northern Water Works Development Agency",
    "search_model": ["auth.User", "tickets.Ticket"],
    "show_sidebar": True,
    "navigation_expanded": True,
    
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index", "permissions": ["auth.view_user"]},
    ],
    
    "show_ui_builder": False,
    "custom_links": {
        "auth": [
            {
                "name": "Forgot Password? Reset Here", 
                "url": "/password-reset/", 
                "icon": "fas fa-key",
            },
        ],
    },
    
    "custom_css": "css/admin_dashboard.css",
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "tickets.Ticket": "fas fa-ticket-alt",
    },
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "navbar": "navbar-dark",
    "sidebar": "sidebar-dark-primary",
}