import os
import json
import uuid
import logging
import datetime
from collections import defaultdict, OrderedDict

import jsonschema
from jsonschema import Draft3Validator, FormatChecker
import scrapelib

from pupa import utils
from pupa import settings
from pupa.exceptions import ScrapeError, ScrapeValueError


@FormatChecker.cls_checks('uri-blank')
def uri_blank(value):
    return value == '' or FormatChecker().conforms(value, 'uri')


@FormatChecker.cls_checks('uri')
def check_uri(val):
    return val and val.startswith(('http://', 'https://', 'ftp://'))


def cleanup_list(obj, default):
    if not obj:
        obj = default
    elif isinstance(obj, str):
        obj = [obj]
    elif not isinstance(obj, list):
        obj = list(obj)
    return obj


class Scraper(scrapelib.Scraper):
    """ Base class for all scrapers """

    def __init__(self, jurisdiction, datadir, *, strict_validation=True, fastmode=False):
        super(Scraper, self).__init__()

        # set options
        self.jurisdiction = jurisdiction
        self.datadir = datadir

        # scrapelib setup
        self.timeout = settings.SCRAPELIB_TIMEOUT
        self.requests_per_minute = settings.SCRAPELIB_RPM
        self.retry_attempts = settings.SCRAPELIB_RETRY_ATTEMPTS
        self.retry_wait_seconds = settings.SCRAPELIB_RETRY_WAIT_SECONDS
        self.verify = settings.SCRAPELIB_VERIFY

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
        """
            Save object to disk as JSON.

            Generally shouldn't be called directly.
        """
        obj.pre_save(self.jurisdiction.jurisdiction_id)

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
            if self.strict_validation:
                raise ve
            else:
                self.warning(ve)

        # after saving and validating, save subordinate objects
        for obj in obj._related:
            self.save_object(obj)

    def do_scrape(self, **kwargs):
        record = {'objects': defaultdict(int)}
        self.output_names = defaultdict(set)
        record['start'] = utils.utcnow()
        for obj in self.scrape(**kwargs) or []:
            if hasattr(obj, '__iter__'):
                for iterobj in obj:
                    self.save_object(iterobj)
            else:
                self.save_object(obj)
        record['end'] = utils.utcnow()
        record['skipped'] = getattr(self, 'skipped', 0)
        if not self.output_names:
            raise ScrapeError('no objects returned from {} scrape'.format(self.__class__.__name__))
        for _type, nameset in self.output_names.items():
            record['objects'][_type] += len(nameset)

        return record

    def latest_session(self):
        return self.jurisdiction.legislative_sessions[-1]['identifier']

    def scrape(self, **kwargs):
        raise NotImplementedError(self.__class__.__name__ + ' must provide a scrape() method')


class BaseBillScraper(Scraper):
    skipped = 0

    class ContinueScraping(Exception):
        """ indicate that scraping should continue without saving an object """
        pass

    def scrape(self, legislative_session, **kwargs):
        self.legislative_session = legislative_session
        for bill_id, extras in self.get_bill_ids(**kwargs):
            try:
                yield self.get_bill(bill_id, **extras)
            except self.ContinueScraping as exc:
                self.warning('skipping %s: %r', bill_id, exc)
                self.skipped += 1
                continue


class BaseModel(object):
    """
    This is the base class for all the Open Civic objects. This contains
    common methods and abstractions for OCD objects.
    """

    # to be overridden by children. Something like "person" or "organization".
    # Used in :func:`validate`.
    _type = None
    _schema = None

    def __init__(self):
        super(BaseModel, self).__init__()
        self._id = str(uuid.uuid1())
        self._related = []
        self.extras = {}

    # validation

    def validate(self, schema=None):
        """
        Validate that we have a valid object.

        On error, this will raise a `ScrapeValueError`

        This also expects that the schemas assume that omitting required
        in the schema asserts the field is optional, not required. This is
        due to upstream schemas being in JSON Schema v3, and not validictory's
        modified syntax.
        ^ TODO: FIXME
        """
        if schema is None:
            schema = self._schema

        type_checker = Draft3Validator.TYPE_CHECKER.redefine(
            "datetime", lambda c, d: isinstance(d, (datetime.date, datetime.datetime))
        )
        type_checker = type_checker.redefine(
            "date", lambda c, d: (isinstance(d, datetime.date)
                                  and not isinstance(d, datetime.datetime))
        )

        ValidatorCls = jsonschema.validators.extend(Draft3Validator, type_checker=type_checker)
        validator = ValidatorCls(schema, format_checker=FormatChecker())

        errors = [str(error) for error in validator.iter_errors(self.as_dict())]
        if errors:
            raise ScrapeValueError('validation of {} {} failed: {}'.format(
                self.__class__.__name__, self._id, '\n\t'+'\n\t'.join(errors)
            ))

    def pre_save(self, jurisdiction_id):
        pass

    def as_dict(self):
        d = {}
        for attr in self._schema['properties'].keys():
            if hasattr(self, attr):
                d[attr] = getattr(self, attr)
        d['_id'] = self._id
        return d

    # operators

    def __setattr__(self, key, val):
        if key[0] != '_' and key not in self._schema['properties'].keys():
            raise ScrapeValueError('property "{}" not in {} schema'.format(key, self._type))
        super(BaseModel, self).__setattr__(key, val)


class SourceMixin(object):
    def __init__(self):
        super(SourceMixin, self).__init__()
        self.sources = []

    def add_source(self, url, *, note=''):
        """ Add a source URL from which data was collected """
        new = {'url': url, 'note': note}
        self.sources.append(new)


class ContactDetailMixin(object):
    def __init__(self):
        super(ContactDetailMixin, self).__init__()
        self.contact_details = []

    def add_contact_detail(self, *, type, value, note=''):
        self.contact_details.append({"type": type, "value": value, "note": note})


class LinkMixin(object):
    def __init__(self):
        super(LinkMixin, self).__init__()
        self.links = []

    def add_link(self, url, *, note=''):
        self.links.append({"note": note, "url": url})


class IdentifierMixin(object):
    def __init__(self):
        super(IdentifierMixin, self).__init__()
        self.identifiers = []

    def add_identifier(self, identifier, *, scheme=''):
        self.identifiers.append({"identifier": identifier, "scheme": scheme})


class OtherNameMixin(object):
    def __init__(self):
        super(OtherNameMixin, self).__init__()
        self.other_names = []

    def add_name(self, name, *, start_date='', end_date='', note=''):
        other_name = {'name': name}
        if start_date:
            other_name['start_date'] = start_date
        if end_date:
            other_name['end_date'] = end_date
        if note:
            other_name['note'] = note
        self.other_names.append(other_name)


class AssociatedLinkMixin(object):
    def _add_associated_link(self, collection, note, url, *, media_type, text, on_duplicate,
                             date=''):
        if on_duplicate not in ['error', 'ignore']:
            raise ScrapeValueError("on_duplicate must be 'error' or 'ignore'")

        try:
            associated = getattr(self, collection)
        except AttributeError:
            associated = self[collection]

        ver = {'note': note, 'links': [], 'date': date}

        # keep a list of the links we've seen, we need to iterate over whole list on each add
        # unfortunately this means adds are O(n)
        seen_links = set()

        matches = 0
        for item in associated:
            for link in item['links']:
                seen_links.add(link['url'])

            if all(ver.get(x) == item.get(x) for x in ["note", "date"]):
                matches = matches + 1
                ver = item

        # it should be impossible to have multiple matches found unless someone is bypassing
        # _add_associated_link
        assert matches <= 1, "multiple matches found in _add_associated_link"

        if url in seen_links:
            if on_duplicate == 'error':
                raise ScrapeValueError("Duplicate entry in '%s' - URL: '%s'" % (collection, url))
            else:
                # This means we're in ignore mode. This situation right here
                # means we should *skip* adding this link silently and continue
                # on with our scrape. This should *ONLY* be used when there's
                # a site issue (Version 1 == Version 2 because of a bug) and
                # *NEVER* because "Current" happens to match "Version 3". Fix
                # that in the scraper, please.
                #  - PRT
                return None

        # OK. This is either new or old. Let's just go for it.
        ret = {'url': url, 'media_type': media_type, 'text': text}

        ver['links'].append(ret)

        if matches == 0:
            # in the event we've got a new entry; let's just insert it into
            # the versions on this object. Otherwise it'll get thrown in
            # automagically.
            associated.append(ver)

        return ver
