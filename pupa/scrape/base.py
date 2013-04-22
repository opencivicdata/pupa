import os
import json
import logging
from collections import defaultdict

import scrapelib

from pupa import utils
from pupa.core import settings


class Scraper(scrapelib.Scraper):
    """ Base class for all scrapers """

    def __init__(self, organization, session,
                 output_dir, cache_dir=None,
                 strict_validation=False, fastmode=False):

        super(Scraper, self).__init__(self)

        # set options
        self.organization = organization
        self.session = session

        # scrapelib setup
        self.timeout = settings.SCRAPELIB_TIMEOUT
        self.requests_per_minute = settings.SCRAPELIB_RPM
        self.retry_attempts = settings.SCRAPELIB_RETRY_ATTEMPTS
        self.retry_wait_seconds = settings.SCRAPELIB_RETRY_WAIT_SECONDS
        self.follow_robots = False

        if fastmode:
            self.requests_per_minute = 0
            self.cache_write_only = False

        # directories
        self.output_dir = output_dir
        self.cache_storage = scrapelib.FileCache(cache_dir)

        # validation
        self.strict_validation = strict_validation

        # 'type' -> {set of names}
        self.output_names = defaultdict(set)

        # logging convenience methods
        self.logger = logging.getLogger("pupa")
        self.info = self.logger.info
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical

    def save_object(self, obj):
        obj_type = obj._schema_name  # XXX: add a _type attribute?
        filename = '{0}_{1}.json'.format(obj_type, obj.uuid)

        self.info('save %s %s as %s', obj_type, obj, filename)

        self.output_names[obj_type].add(filename)

        with open(os.path.join(self.output_dir, filename),
                  'w') as f:
            json.dump(obj.as_dict(), f, cls=utils.JSONEncoderPlus)

        # validate after writing, allows for inspection on failure
        try:
            obj.validate()
        except ValueError as ve:
            self.warning(ve)
            if self.strict_validation:
                raise ve

    def scrape_types(self, obj_types):
        if 'person' in obj_types:
            self.scrape_people()
        # XXX: other types

    def scrape_people(self):
        for obj in self.get_people():
            self.save_object(obj)

    def get_people(self):
        raise NotImplementedError(self.__class__.__name__ + ' must provide a '
                                  'get_people() method or override '
                                  'scrape_people()')
