import os
import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgres://pupa:pupa@localhost/opencivicdata')
SECRET_KEY = 'non-secret'
INSTALLED_APPS = ('pupa',)

# data enumerations

ORGANIZATION_CLASSIFICATIONS = ['legislature', 'party', 'committee', 'commission']
BILL_TYPES = ['bill', 'resolution', 'concurrent resolution', 'joint resolution', 'memorial']
BILL_ACTION_TYPES = ['introduced', 'reading:1', 'reading:2', 'reading:3']
BILL_RELATION_TYPES = ["companion", "other-session", "replaced-by", "replaces"]
VERSION_TYPES = []
DOCUMENT_TYPES = []
CONTACT_TYPES = ['address', 'email', 'fax', 'voice']

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

# Django settings
DEBUG = False
TEMPLATE_DEBUG = False

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

try:
    from pupa_settings import *     # NOQA
except ImportError:
    print('no pupa_settings on path, using defaults')
    pass


DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
