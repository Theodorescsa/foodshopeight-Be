from .base import *

# Prod mà :>
DEBUG = True

# Khi CHƯA có HTTPS qua Nginx/certbot thì KHÔNG redirect https
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Tối thiểu IP server (hoặc domain) – đừng để '*'
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ['*']

# DB giữ nguyên phần bạn dùng env PROD
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
