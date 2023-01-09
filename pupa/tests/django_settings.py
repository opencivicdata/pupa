# django settings for tests
SECRET_KEY = 'test'
INSTALLED_APPS = ('django.contrib.contenttypes',
                  'opencivicdata.core.apps.BaseConfig',
                  'opencivicdata.legislative.apps.BaseConfig',
                  'pupa')
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'test',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': 32001,
    }
}
MIDDLEWARE_CLASSES = ()
