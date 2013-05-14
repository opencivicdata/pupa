import os
import json
import logging
from collections import defaultdict

import scrapelib

from larvae.membership import Membership
from pupa import utils
from pupa.core import settings



class Scraper(scrapelib.Scraper):
    """ Base class for all scrapers """

    class ContinueScraping(Exception):
        """ indicate that scraping should continue without saving an object """
        pass

    def __init__(self, jurisdiction, session, output_dir, cache_dir=None,
                 strict_validation=True, fastmode=False):

        super(Scraper, self).__init__(self)

        self.skipped = 0

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
        if cache_dir:
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
        if hasattr(obj, '_is_legislator'):
            membership = Membership(
                obj._id, 'jurisdiction:' + self.jurisdiction.jurisdiction_id,
                district=obj.district, chamber=obj.chamber,
                contact_details=obj._contact_details, role='member')
            # remove placeholder _contact_details
            del obj._contact_details
            obj._related.append(membership)

            # create a party membership
            if obj.party:
                membership = Membership(obj._id,
                                        'party:' + obj.party,
                                        role='member')
                obj._related.append(membership)

        filename = '{0}_{1}.json'.format(obj._type, obj._id)

        self.info('save %s %s as %s', obj._type, obj, filename)

        self.output_names[obj._type].add(filename)

        with open(os.path.join(self.output_dir, filename), 'w') as f:
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

    def scrape_types(self, scraper_types):
        if 'person' in scraper_types:
            self.scrape_people()
        if 'bill' in scraper_types:
            self.scrape_bills()

    def scrape_people(self):
        for obj in self.get_people():
            if hasattr(obj, '__iter__'):
                for iterobj in obj:
                    self.save_object(iterobj)
            else:
                self.save_object(obj)

    def scrape_bills(self):
        for obj in self.get_bills():
            if hasattr(obj, '__iter__'):
                for iterobj in obj:
                    self.save_object(iterobj)
            else:
                self.save_object(obj)

    def get_bills(self):
        for bill_id, extras in self.get_bill_ids():
            try:
                yield self.get_bill(bill_id, **extras)
            except self.ContinueScraping as exc:
                self.warning('skipping %s: %r', bill_id, exc)
                self.skipped += 1
                continue

    def get_people(self):
        raise NotImplementedError(self.__class__.__name__ + ' must provide a '
                                  'get_people() method')

    def get_bill_ids(self):
        raise NotImplementedError(self.__class__.__name__ + ' must provide a '
                                  'get_bill_ids() method or override '
                                  'get_bills()')

    def get_bill(self, bill_id, **kwargs):
        raise NotImplementedError(self.__class__.__name__ + ' must provide a '
                                  'get_bill() method or override '
                                  'get_bills()')
