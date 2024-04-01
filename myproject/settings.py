﻿"""
Django settings for myproject project.

Generated by 'django-admin startproject' using Django 4.2.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-=a(k-rq5(i)hd%l6sdedxx^9@li#i^n=zs%4+oq7wwypny)81+"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "web",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'ckeditor',
    'ckeditor_uploader',
    'django_crontab',
    'user_sessions',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware"
    
]

ROOT_URLCONF = "myproject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'websql',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': '3306',
        # 取消对外键的检查
        'OPTIONS':{
        "init_command":"SET foreign_key_checks = 0;",
        }
    }
    
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = False


# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',  # 工具条功能
        'height': 300,  # 编辑器高度
        'width': 800,  # 编辑器宽
        'toolbar_Custom': [
            ['Source','Bold', 'Italic', 'Underline', 'Blockquote','Format','Font','FontSize'],
            ['TextColor','BGColor','Image','Smiley' ,'Link', 'Unlink','PasteFromWord'],
            ['JustifyCenter','JustifyRight','JustifyBlock']
        ],
        'pasteFilter': 'plain-text-and-urls; max-width 100%; max-height 100%;',
    },
}


CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024  # 设置为 20 MB
