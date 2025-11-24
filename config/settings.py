"""
Configuración de Django para el proyecto config.

Generado por 'django-admin startproject' usando Django 3.2.12.

Para más información sobre este archivo, ver
https://docs.djangoproject.com/en/3.2/topics/settings/

Para la lista completa de configuraciones y sus valores, ver
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde archivo .env
load_dotenv()

# Construir rutas dentro del proyecto así: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Configuración de desarrollo de inicio rápido - no adecuada para producción
# Ver https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# ADVERTENCIA DE SEGURIDAD: ¡mantenga en secreto la clave secreta usada en producción!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-z+r%h!g^)uw=wv72znlk#5vt#*ml#316(gmjm2m-!9yrb*^pc$')

# ADVERTENCIA DE SEGURIDAD: ¡no ejecute con debug activado en producción!
DEBUG = True

ALLOWED_HOSTS = []

# Definición de la aplicación

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'ingesta',
    'coreview',
    'reports',
    'paa',
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'coreview' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'coreview.context_processors.global_template_context',
                'accounts.context_processors.permissions',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Base de datos
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'uaesp_dev_db',
        'USER': 'uaesp_dev_user',
        'PASSWORD': 'password_db',
        'HOST': 'db',  # Esta es la parte importante - usar 'db' en lugar de 'localhost'
        'PORT': '5432',
    }
}


# Validación de contraseñas
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internacionalización
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Archivos estáticos (CSS, JavaScript, Imágenes)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Lugares extra para que collectstatic encuentre archivos estáticos.
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Tipo de campo de clave primaria predeterminado
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/ingesta/dashboard/' # A donde ir tras login exitoso
LOGOUT_REDIRECT_URL = '/'