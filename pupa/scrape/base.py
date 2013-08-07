import os
import json
import logging
import datetime
from collections import defaultdict

import scrapelib

from larvae.membership import Membership
from pupa import utils
from pupa.core import settings


class ScrapeError(Exception):
    pass


class Scraper(scrapelib.Scraper):
    """ Base class for all scrapers """

    class ContinueScraping(Exception):
        """ indicate that scraping should continue without saving an object """
        pass

    def __init__(self, jurisdiction, session, output_dir, cache_dir=None,
                 strict_validation=True, fastmode=False):

        super(Scraper, self).__init__()

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

    def get_current_session(self):
        j = self.jurisdiction.get_metadata()
        current_term = j['terms'][0]
        current_session = current_term['sessions'][-1]
        return current_session

    def save_object(self, obj):
        if hasattr(obj, '_is_legislator'):
            membership = Membership(
                obj._id, 'jurisdiction:' + self.jurisdiction.jurisdiction_id,
                post_id=obj.post_id, chamber=obj.chamber,
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

    def _scrape(self, iterable, scrape_type):
        record = {'objects': defaultdict(int)}
        self.output_names = defaultdict(set)
        record['start'] = datetime.datetime.utcnow()
        for obj in iterable:
            if hasattr(obj, '__iter__'):
                for iterobj in obj:
                    self.save_object(iterobj)
            else:
                self.save_object(obj)
        record['end'] = datetime.datetime.utcnow()
        if not self.output_names:
            raise ScrapeError("no objects returned from {0} scrape".format(
                scrape_type))
        for _type, nameset in self.output_names.items():
            record['objects'][_type] += len(nameset)

        return {scrape_type: record}

    def scrape_people(self):
        return self._scrape(self.get_people(), 'people')

    def scrape_bills(self):
        return self._scrape(self.get_bills(), 'bills')

    def scrape_votes(self):
        return self._scrape(self.get_votes(), 'votes')

    def scrape_events(self):
        return self._scrape(self.get_events(), 'events')

    def scrape_speeches(self):
        return self._scrape(self.get_speeches(), 'speeches')

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

    def get_events(self):
        raise NotImplementedError(self.__class__.__name__ + ' must provide a '
                                  'get_events() method')

    def get_votes(self):
        raise NotImplementedError(self.__class__.__name__ + ' must provide a '
                                  'get_votes() method')

    def get_speeches(self):
        raise NotImplementedError(self.__class__.__name__ + ' must provide a '
                                  'get_speeches() method')
