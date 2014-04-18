from .base import BaseModel
from .schemas.jurisdiction import schema


class Jurisdiction(BaseModel):
    """ Base class for a jurisdiction """

    _type = 'jurisdiction'
    _schema = schema
    _collection = 'jurisdictions'

    # schema objects
    name = None
    url = None
    sessions = []
    feature_flags = []
    building_maps = []
    other_names = []
    _meta = {}

    # non-db properties
    scrapers = {}
    default_scrapers = {}
    organizations = []
    parties = []
    parent_id = None
    ignored_scraped_sessions = []

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    # add _id property to mimic other types without a user-set ID

    @property
    def _id(self):
        return self.jurisdiction_id

    @_id.setter
    def _id(self, val):
        self.jurisdiction_id = val

    def as_dict(self):
        return {'_type': self._type, '_id': self._id, '_meta': self._meta,
                'name': self.name, 'url': self.url,
                'sessions': self.sessions, 'feature_flags': self.feature_flags,
                'building_maps': self.building_maps}

    def get_organization(self, chamber=None, party=None):
        if chamber:
            for org in self.organizations:
                if org['chamber'] == chamber:
                    return org
            raise ValueError('no such chamber: ' + chamber)
        if party:
            for org in self.parties:
                if org['name'] == party:
                    return org
            return ValueError('no such party: ' + party)
        pass

    def get_session_list(self):
        raise NotImplementedError('get_session_list is not implemented')

    def extract_text(self):
        raise NotImplementedError('extract_text is not implemented')

    def __str__(self):
        return self.name
    __unicode__ = __str__
