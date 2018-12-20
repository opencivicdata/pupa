import os
import sys
import importlib

import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgis://pupa:pupa@localhost/opencivicdata')
SECRET_KEY = 'non-secret'
INSTALLED_APPS = ('django.contrib.contenttypes',
                  'opencivicdata.core.apps.BaseConfig',
                  'opencivicdata.legislative.apps.BaseConfig',
                  'pupa')

# scrape settings

SCRAPELIB_RPM = 60
SCRAPELIB_TIMEOUT = 60
SCRAPELIB_RETRY_ATTEMPTS = 3
SCRAPELIB_RETRY_WAIT_SECONDS = 10
SCRAPELIB_VERIFY = True

CACHE_DIR = os.path.join(os.getcwd(), '_cache')
SCRAPED_DATA_DIR = os.path.join(os.getcwd(), '_data')

# import settings

ENABLE_PEOPLE_AND_ORGS = True
ENABLE_BILLS = True
ENABLE_VOTES = True
ENABLE_EVENTS = True

IMPORT_TRANSFORMERS = {
    'bill': []
}

# Django settings
DEBUG = False
TEMPLATE_DEBUG = False

MIDDLEWARE_CLASSES = ()
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "%(asctime)s %(levelname)s %(name)s: %(message)s",
            'datefmt': '%H:%M:%S'
        }
    },
    'handlers': {
        'default': {'level': 'DEBUG',
                    'class': 'pupa.ext.ansistrm.ColorizingStreamHandler',
                    'formatter': 'standard'},
    },
    'loggers': {
        '': {
            'handlers': ['default'], 'level': 'DEBUG', 'propagate': True
        },
        'scrapelib': {
            'handlers': ['default'], 'level': 'INFO', 'propagate': False
        },
        'requests': {
            'handlers': ['default'], 'level': 'WARN', 'propagate': False
        },
        'boto': {
            'handlers': ['default'], 'level': 'WARN', 'propagate': False
        },
    },
}


sys.path.insert(1, os.getcwd())
loader = importlib.util.find_spec('pupa_settings')
if loader is None:
    print('no pupa_settings on path, using defaults')
else:
    from pupa_settings import *     # NOQA


DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
