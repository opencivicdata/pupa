MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DATABASE = 'opencivicdata'

SCRAPELIB_RPM = 60
SCRAPELIB_TIMEOUT = 60
SCRAPELIB_RETRY_ATTEMPTS = 3
SCRAPELIB_RETRY_WAIT_SECONDS = 20

ENABLE_ELASTICSEARCH = False
ELASTICSEARCH_HOST = 'localhost'
ELASTICSEARCH_TIMEOUT = 2

BILL_FILTERS = {}
LEGISLATOR_FILTERS = {}
EVENT_FILTERS = {}

LOGGING_CONFIG = {
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
