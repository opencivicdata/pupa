from .base import BaseModel
from .schemas.jurisdiction import schema
from .organization import Organization


class Jurisdiction(BaseModel):
    """ Base class for a jurisdiction """

    _type = 'jurisdiction'
    _schema = schema
    _collection = 'jurisdictions'

    # schema objects
    name = None
    url = None
    chambers = {}
    sessions = []
    feature_flags = []
    building_maps = []
    other_names = []

    # non-db properties
    scrapers = {}
    default_scrapers = {}
    parties = []
    parent_id = None
    ignored_scraped_sessions = []

    def as_dict(self):
        return {'_type': self._type, 'name': self.name, 'url': self.url, 'chambers': self.chambers,
                'sessions': self.sessions, 'feature_flags': self.feature_flags,
                'building_maps': self.building_maps}

    def get_session_list(self):
        raise NotImplementedError('get_session_list is not implemented')

    def extract_text(self):
        raise NotImplementedError('extract_text is not implemented')

    def __str__(self):
        return self.name
    __unicode__ = __str__
