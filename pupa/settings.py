import os
import importlib
import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgis://pupa:pupa@localhost/opencivicdata')
SECRET_KEY = 'non-secret'
INSTALLED_APPS = ('opencivicdata.apps.BaseConfig', 'pupa',)

# scrape settings

SCRAPELIB_RPM = 60
SCRAPELIB_TIMEOUT = 60
SCRAPELIB_RETRY_ATTEMPTS = 3
SCRAPELIB_RETRY_WAIT_SECONDS = 20

CACHE_DIR = os.path.join(os.getcwd(), '_cache')
SCRAPED_DATA_DIR = os.path.join(os.getcwd(), '_data')

ENABLE_ELASTICSEARCH = False
ELASTICSEARCH_HOST = 'localhost'
ELASTICSEARCH_TIMEOUT = 2

# dump settings

API_KEY = os.environ.get('PUPA_API_KEY', None)
AWS_KEY = os.environ.get('AWS_KEY', None)
AWS_SECRET = os.environ.get('AWS_SECRET', None)

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


loader = importlib.find_loader('pupa_settings')
if loader is None:
    print('no pupa_settings on path, using defaults')
else:
    from pupa_settings import *     # NOQA


DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
