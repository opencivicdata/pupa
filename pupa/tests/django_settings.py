# django settings for tests
SECRET_KEY = 'test'
INSTALLED_APPS = ('opencivicdata',)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.gis.backends.postgis',
        'NAME': 'test',
        'USER': 'test',
        'PASSWORD': 'test',
        'HOST': 'localhost',
    }
}
