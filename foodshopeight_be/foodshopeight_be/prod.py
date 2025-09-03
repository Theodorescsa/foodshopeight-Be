from .base import *
DEBUG = True
SECURE_SSL_REDIRECT = True
# Nếu muốn chuyển địa chỉ trang web hoặc muốn tạo 1 đường dẫn mới thì copy và tạo như folder này, sau đó gán vào - tieplv
ALLOWED_HOSTS = ['*']
# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env("NAME_PROD"),
        'HOST': env("HOST_PROD"),
        'PORT': env("PORT_PROD"),
        'USER':  env("USER_PROD"),
        'PASSWORD': env("PASSWORD_PROD"),
        'OPTIONS': {
            'sql_mode': 'STRICT_TRANS_TABLES',
            'charset': 'utf8mb4',
            'use_unicode': True,
        }
    }
}