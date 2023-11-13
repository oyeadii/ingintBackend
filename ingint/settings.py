import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-sir-c35521tqz9=hwjw_4_112cft^#fd^vby!$h!^bhk_v)^l5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TIMEOUT = 1200
ALLOWED_HOSTS = ['*']


# Application definition
CUSTOM_APPS =[
    "data_analytics",
    "user"
]
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]+CUSTOM_APPS

MIGRATION_MODULES = {
    **{'auth': None,
    'admin':None,
    'contenttypes': None,
    'sessions': None,},
    **{x:None for x in CUSTOM_APPS}
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'custom_lib.custom_middleware.ErrorHandlerMiddleware',
]

ROOT_URLCONF = 'ingint.urls'

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

WSGI_APPLICATION = 'ingint.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
envs = os.environ
HOST_SERVER = envs.get("HOST_SERVER","http://localhost:8000")
DB_NAME = envs.get("DB_NAME","")
DB_USER = envs.get("DB_USER","")
DB_PASSWORD = envs.get("DB_PASSWORD","")
DB_SERVER = envs.get("DB_SERVER","")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER':DB_USER,
        'PASSWORD':DB_PASSWORD,
        'HOST':DB_SERVER,
        'PORT':3306,
        'CONN_MAX_AGE':None
    }
}

# Password validation
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

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'custom_lib.authentication.ClientAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': ['custom_lib.renderer.JSONResponseRenderer'],
    'ADDITIONAL_JSON_RENDERER_CLASSES': ['custom_lib.renderer.DataAnalysisResponseRenderer',],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'api_key': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            "description": "JWT authorization"
        }, 'basic': {
            'type': 'basic'
        }
    },
    'JSON_EDITOR': True,
    'TAGS_SORTER':'alpha',
    # 'FILTER':'tags'
    'MAX_DISPLAYED_TAGS':1
}

ERROR_FILE_PATH=os.path.join(BASE_DIR,"error_code.json")
ERROR_JSON={}
try:
    ERROR_JSON = json.loads(open(ERROR_FILE_PATH).read())
except Exception as e:
    print(e)

CORS_ORIGIN_ALLOW_ALL = True
from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + ['token','newToken',"userId","X-Frontend-Domain"]


# common env variables
ENVI = envs.get("ENVI")
LOG_DELETION=int(envs.get('LOG_DELETION_DAY', 15))
JWT_EXPIRATION_IN_MINUTES=envs.get("JWT_EXPIRATION_IN_MINUTES")
ALLOWED_EXTENSION=envs.get("ALLOWED_EXTENSION", "")
DEFAULT_FILE_STORAGE = envs.get("DEFAULT_FILE_STORAGE", "django.core.files.storage.FileSystemStorage")
# files management
AWS_S3_ACCESS_KEY_ID = envs.get("AWS_S3_ACCESS_KEY_ID", "")
AWS_S3_SECRET_ACCESS_KEY = envs.get("AWS_S3_SECRET_ACCESS_KEY", "")
AWS_BUCKET_NAME = envs.get("AWS_FILE_STORAGE_BUCKET_NAME", "")
AWS_S3_REGION_NAME = envs.get("AWS_S3_REGION_NAME", "")
AWS_DEFAULT_ACL = envs.get("AWS_DEFAULT_ACL", "private")
# vectordb creds
PINECONE_KEY=envs.get("PINECONE_KEY","")
PINECONE_ENV=envs.get("PINECONE_ENV","")
PINECONE_INDEX_NAME=envs.get("PINECONE_INDEX_NAME","")
# openai confugs
OPENAI_API_KEY=envs.get("OPENAI_API_KEY")
MODEL_EMBEDDING=envs.get("MODEL_EMBEDDING")
MODEL_MAX_INPUT_SIZE=int(envs.get("MODEL_MAX_INPUT_SIZE"))
MODEL_NUM_OUTPUTS=int(envs.get("MODEL_NUM_OUTPUTS"))
MODEL_MAX_CHUNK_OVERLAP=int(envs.get("MODEL_MAX_CHUNK_OVERLAP"))
MODEL_CHUNK_SIZE_LIMIT=int(envs.get("MODEL_CHUNK_SIZE_LIMIT"))