import os
import json
import logging
from collections import defaultdict

import scrapelib

from pupa import utils
from pupa.core import settings


class Scraper(scrapelib.Scraper):
    """ Base class for all scrapers """

    def __init__(self, jurisdiction, session, output_dir, cache_dir=None,
                 strict_validation=False, fastmode=False):

        super(Scraper, self).__init__(self)

        # set options
        self.jurisdiction = jurisdiction
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
        if obj._type == 'legislator':
            seat_post = self.jurisdiction.get_post_id(district=obj.district,
                                                      chamber=obj.chamber)
            obj.add_membership(self.jurisdiction.organization_id,
                               post_id=seat_post)   #, role='member')
            party = self.jurisdiction.get_party(obj.party)
            obj.add_membership(party)
        # XXX: add custom save logic as needed
        #elif obj._type in ('instrument', ...):

        filename = '{0}_{1}.json'.format(obj._type, obj._id)

        self.info('save %s %s as %s', obj._type, obj, filename)

        self.output_names[obj._type].add(filename)

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

        # after saving and validating, save subordinate objects
        for obj in getattr(obj, '_related', []):
            self.save_object(obj)

    def scrape_types(self, obj_types):
        if 'person' in obj_types:
            self.scrape_people()

    def scrape_people(self):
        for obj in self.get_people():
            if hasattr(obj, '__iter__'):
                for iterobj in obj:
                    self.save_object(iterobj)
            else:
                self.save_object(obj)

    def get_people(self):
        raise NotImplementedError(self.__class__.__name__ + ' must provide a '
                                  'get_people() method or override '
                                  'scrape_people()')
