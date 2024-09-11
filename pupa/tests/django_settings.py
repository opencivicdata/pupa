# django settings for tests
import os

SECRET_KEY = 'test'
INSTALLED_APPS = ('django.contrib.contenttypes',
                  'opencivicdata.core.apps.BaseConfig',
                  'opencivicdata.legislative.apps.BaseConfig',
                  'pupa')
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.getenv('POSTGRES_DB', 'test'),
        'USER': os.getenv('POSTGRES_USER', 'test'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'test'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', 5432),
    }
}
MIDDLEWARE_CLASSES = ()
