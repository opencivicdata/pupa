import os
import dj_database_url

SECRET_KEY = 'non-secret'
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgres://pupa:pupa@localhost/opencivicdata')
INSTALLED_APPS = ('pupa',)

DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
