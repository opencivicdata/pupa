import uuid
from .utils import DatetimeValidator


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
        self._meta = {}
        self.extras = {}

    # validation

    def validate(self, schema=None):
        """
        Validate that we have a valid object.

        On error, this will either raise a `ValueError` or a
        `validictory.ValidationError` (a subclass of `ValueError`).

        This also expects that the schemas assume that omitting required
        in the schema asserts the field is optional, not required. This is
        due to upstream schemas being in JSON Schema v3, and not validictory's
        modified syntax.
        """
        if schema is None:
            schema = self._schema

        validator = DatetimeValidator(required_by_default=False)
        validator.validate(self.as_dict(), schema)

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
            raise ValueError('property "{}" not in {} schema'.format(key, self._type))
        super(BaseModel, self).__setattr__(key, val)

    def __eq__(self, other):
        """ equality requires all fields to be equal except for the _id """
        sd = self.as_dict()
        od = other.as_dict()
        sd.pop('_id')
        od.pop('_id')
        return sd == od


class SourceMixin(object):
    def __init__(self):
        super(SourceMixin, self).__init__()
        self.sources = []

    def add_source(self, url, note='', **kwargs):
        """ Add a source URL from which data was collected """
        new = kwargs.copy()
        new.update({'url': url, 'note': note})
        self.sources.append(new)


class ContactDetailMixin(object):
    def __init__(self):
        super(ContactDetailMixin, self).__init__()
        self.contact_details = []

    def add_contact_detail(self, type, value, note):
        self.contact_details.append({"type": type, "value": value, "note": note})


class LinkMixin(object):
    def __init__(self):
        super(LinkMixin, self).__init__()
        self.links = []

    def add_link(self, url, note=''):
        self.links.append({"note": note, "url": url})


class AssociatedLinkMixin(object):
    def _add_associated_link(self, collection, name, url, type, mimetype, on_duplicate, date=None,
                             offset=None, document_id=None):
        if on_duplicate not in ['error', 'ignore']:
            raise ValueError("on_duplicate must be 'error' or 'ignore'")

        try:
            versions = getattr(self, collection)
        except AttributeError:
            versions = self[collection]

        ver = {'name': name, 'links': [], 'date': date, 'offset': offset, 'type': type,
               'document_id': document_id}

        seen_links = set()
        # We iterate over everything anyway. Meh. Storing
        # as an instance var is actually non-trivial, since we abuse __slots__
        # for as_dict, and it's otherwise read-only or shared set() instance.

        matches = 0
        for version in versions:
            for link in version['links']:
                seen_links.add(link['url'])

            if all(ver.get(x) == version.get(x) for x in ["name", "type", "date"]):
                matches = matches + 1
                ver = version

        if matches > 1:
            raise ValueError("multiple matches found in _add_associated_link")

        if url in seen_links:
            if on_duplicate == 'error':
                raise ValueError("Duplicate entry in '%s' - URL: '%s'" % (collection, url))
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
        ret = {'url': url, 'mimetype': mimetype}

        ver['links'].append(ret)

        if matches == 0:
            # in the event we've got a new entry; let's just insert it into
            # the versions on this object. Otherwise it'll get thrown in
            # automagically.
            versions.append(ver)

        return ver
