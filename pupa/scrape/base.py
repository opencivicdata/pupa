import os
import json
import logging
import datetime
from collections import defaultdict, OrderedDict

import scrapelib

from pupa import utils
from pupa.models import Membership, Organization
from pupa.core import settings


class ScrapeError(Exception):
    pass


class Scraper(scrapelib.Scraper):
    """ Base class for all scrapers """

    def __init__(self, jurisdiction, datadir, strict_validation=True, fastmode=False):
        super(Scraper, self).__init__()

        # set options
        self.jurisdiction = jurisdiction
        self.datadir = datadir

        # scrapelib setup
        self.timeout = settings.SCRAPELIB_TIMEOUT
        self.requests_per_minute = settings.SCRAPELIB_RPM
        self.retry_attempts = settings.SCRAPELIB_RETRY_ATTEMPTS
        self.retry_wait_seconds = settings.SCRAPELIB_RETRY_WAIT_SECONDS
        self.follow_robots = False

        # caching
        if settings.CACHE_DIR:
            self.cache_storage = scrapelib.FileCache(settings.CACHE_DIR)

        if fastmode:
            self.requests_per_minute = 0
            self.cache_write_only = False

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
                post_id=obj.post_id, chamber=obj.chamber,
                contact_details=obj._contact_details, role=obj._role)
            # remove placeholder _contact_details
            del obj._contact_details
            del obj._role
            obj._related.append(membership)

            # create a party membership
            if obj.party:
                membership = Membership(obj._id, 'party:' + obj.party, role='member')
                obj._related.append(membership)

        filename = '{0}_{1}.json'.format(obj._type, obj._id).replace('/', '-')

        self.info('save %s %s as %s', obj._type, obj, filename)
        self.debug(json.dumps(OrderedDict(sorted(obj.as_dict().items())),
                              cls=utils.JSONEncoderPlus, indent=4, separators=(',', ': ')))

        self.output_names[obj._type].add(filename)

        with open(os.path.join(self.datadir, filename), 'w') as f:
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

    def do_scrape(self, **kwargs):
        record = {'objects': defaultdict(int)}
        self.output_names = defaultdict(set)
        record['start'] = datetime.datetime.utcnow()
        for obj in self.scrape(**kwargs) or []:
            if hasattr(obj, '__iter__'):
                for iterobj in obj:
                    self.save_object(iterobj)
            else:
                self.save_object(obj)
        record['end'] = datetime.datetime.utcnow()
        record['skipped'] = getattr(self, 'skipped', 0)
        if not self.output_names:
            raise ScrapeError('no objects returned from scrape')
        for _type, nameset in self.output_names.items():
            record['objects'][_type] += len(nameset)

        return record

    def scrape(self, **kwargs):
        raise NotImplementedError(self.__class__.__name__ + ' must provide a scrape() method')


class BaseBillScraper(Scraper):
    skipped = 0

    class ContinueScraping(Exception):
        """ indicate that scraping should continue without saving an object """
        pass

    def scrape(self, session, **kwargs):
        self.session = session
        for bill_id, extras in self.get_bill_ids(**kwargs):
            try:
                yield self.get_bill(bill_id, **extras)
            except self.ContinueScraping as exc:
                self.warning('skipping %s: %r', bill_id, exc)
                self.skipped += 1
                continue


class JurisdictionScraper(Scraper):
    def scrape(self):
        # yield a single Jurisdiction object
        yield self.jurisdiction

        # if organizations weren't specified yield one top-level org
        if not self.jurisdiction.organizations:
            org = Organization(name=self.jurisdiction.name, classification='legislature',
                               jurisdiction_id=self.jurisdiction.jurisdiction_id)
            org.add_source(self.jurisdiction.url)
            yield org
        else:
            for chamber, properties in jurisdiction.chambers.items():
                org = Organization(classification='party', name=properties['name'],
                                   chamber=chamber, parent_id=parent_id,
                                   jurisdiction_id=self.jurisdiction.jurisdiction_id)
                org.add_source(self.jurisdiction.url)
                yield org

        for party in self.jurisdiction.parties:
            org = Organization(classification='party', name=party['name'])
            org.add_source(self.jurisdiction.url)
            yield org
