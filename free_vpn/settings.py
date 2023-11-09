from pathlib import Path
import environ
import dj_database_url

env = environ.Env(

    DEBUG=(bool, False)
)

DEBUG = env.bool('DEBUG', False)


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.str('SECRET_KEY', '')

ALLOWED_HOSTS = [
    '*',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'free_vpn.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'free_vpn.wsgi.application'

DATABASE_URL = env.str('DATABASE_URL', None) or (
        f"postgres://{env.str('DB_USER')}:{env.str('DB_PASS')}" 
        f"@{env.str('DB_HOST')}:{env.str('DB_PORT')}" 
        f"/{env.str('DB_NAME')}"
)
        
DATABASES = {
    'default':  dj_database_url.config(default=DATABASE_URL)
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

APPS = [
    'app',
]

STATIC_URL = 'static/'
STATIC_ROOT = Path.joinpath(BASE_DIR, STATIC_URL)

STATICFILES_DIRS = [
   Path.joinpath(BASE_DIR, app, STATIC_URL) for app in APPS
]



DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
