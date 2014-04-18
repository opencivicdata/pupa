import os
import sys
import logging
import logging.config

from . import default_settings


class Settings(object):
    def __init__(self):
        pass

    def __setattr__(self, attr, val):
        super(Settings, self).__setattr__(attr, val)
        # if logging config is changed, reconfigure logging
        if attr == 'LOGGING_CONFIG':
            logging.config.dictConfig(self.LOGGING_CONFIG)

    def update(self, module):
        if isinstance(module, dict):
            for setting, val in module.items():
                if setting.isupper() and val is not None:
                    setattr(self, setting, val)
        else:
            for setting in dir(module):
                if setting.isupper():
                    val = getattr(module, setting)
                    if val is not None:
                        setattr(self, setting, val)

settings = Settings()
settings.update(default_settings)

try:
    sys.path.insert(0, os.getcwd())
    import pupa_settings
    settings.update(pupa_settings)
    sys.path.pop(0)
except ImportError:
    logging.warning('no pupa_settings file found, continuing with defaults..')

elasticsearch = None


class ErrorProxy(object):
    def __init__(self, error):
        self.error = error

    def __getattr__(self, attr):
        raise self.error
    __getitem__ = __getattr__


def _configure_es(host, timeout):
    import pyelasticsearch
    global elasticsearch
    try:
        elasticsearch = pyelasticsearch.ElasticSearch(host, timeout=timeout, revival_delay=0)
    except Exception as e:
        elasticsearch = ErrorProxy(e)


if settings.ENABLE_ELASTICSEARCH:
    _configure_es(settings.ELASTICSEARCH_HOST, settings.ELASTICSEARCH_TIMEOUT)
