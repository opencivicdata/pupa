import uuid
from .utils import DatetimeValidator
from pupa.core import db


class BaseModel(object):
    """
    This is the base class for all the Open Civic objects. This contains
    common methods and abstractions for OCD objects.
    """

    # needs slots defined so children __slots__ are enforced
    __slots__ = ('_id', '_related', 'sources', 'created_at', 'updated_at', 'extras', '_meta')

    # to be overridden by children. Something like "person" or "organization".
    # Used in :func:`validate`.
    _type = None
    _schema = None

    def __init__(self):
        self._id = str(uuid.uuid1())
        self._related = []
        self.sources = []
        self.extras = {}
        self._meta = {}

    # scraping helpers

    def add_extra(self, key, value):
        self.extras[key] = value

    def add_meta(self, key, value):
        self._meta[key] = value

    def add_meta_software(self, name):
        self.add_meta('software', name)

    def add_source(self, url, note=None, **kwargs):
        """ Add a source URL from which data was collected """
        new = kwargs.copy()
        new.update({'url': url, 'note': note})
        self.sources.append(new)

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

    # from/to dict

    @classmethod
    def from_dict(cls, db_obj):
        db_obj = db_obj.copy()
        _type = db_obj.pop('_type')

        # hack to get location set correctly since constructor mangles it
        if _type == 'event':
            location = db_obj.pop('location')
            db_obj['location'] = None

        if _type == 'vote':
            # Hack to deal with Vote mangling. We abstract away the
            # counts so that scrapers don't have to deal with it. This
            # isn't great, but kinda needed.
            counts = db_obj['vote_counts']
            for count in counts:
                db_obj[{
                    "yes": "yes_count",
                    "no": "no_count",
                    "other": "other_count"
                }[count['vote_type']]] = count['count']

        try:
            newobj = cls(**db_obj)
        except TypeError:
            # OK. Let's try to save some good debug information.
            print("Error: Signature doesn't match object on disk.")
            print("We're trying to create a: %s" % (cls.__name__))
            print("Dump of keys from object:")
            for key in db_obj.keys():
                print("  %s" % (key))
            print("This can mean that you have a stale scraped_data folder")
            print("Please remove it and re-try the scrape.")
            print("")
            print("Object in question:")
            print("  %s" % (db_obj.get('_id')))
            print("")
            raise

        # set correct location object after creation
        if _type == 'event':
            newobj.location = location

        return newobj

    def as_dict(self):
        d = {}
        all_slots = set(self.__slots__)
        for cls in self.__class__.__mro__:
            all_slots |= set(cls.__slots__)
            if cls == BaseModel:
                break
        for attr in all_slots:
            if attr != '_related' and hasattr(self, attr):
                d[attr] = getattr(self, attr)
        d['_type'] = self._type
        return d

    # database stuff
    def save(self):
        db[self._collection].save(self.as_dict())

    # operators

    def __eq__(self, other):
        """ equality requires all fields to be equal except for the _id """
        sd = self.as_dict()
        od = other.as_dict()
        sd.pop('_id')
        od.pop('_id')
        return sd == od
