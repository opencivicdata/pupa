from .base import BaseModel, Scraper
from .schemas.jurisdiction import schema
from .popolo import Organization


class Jurisdiction(BaseModel):
    """ Base class for a jurisdiction """

    _type = 'jurisdiction'
    _schema = schema

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
    posts = []
    parties = []
    parent_id = None
    ignored_scraped_sessions = []

    def __init__(self, **kwargs):
        super(Jurisdiction, self).__init__()

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
        return {'_id': self._id, 'id': self._id, 'name': self.name, 'url': self.url,
                'sessions': self.sessions,
                'feature_flags': self.feature_flags,
                'building_maps': self.building_maps}

    #def get_organization(self, chamber=None, party=None):
    #    if chamber:
    #        for org in self.organizations:
    #            if org.chamber == chamber:
    #                return org
    #        raise ValueError('no such chamber: ' + chamber)
    #    if party:
    #        for pname in self.parties:
    #            if p['name'] == party:
    #                return org
    #        raise ValueError('no such party: ' + party)

    def get_session_list(self):
        raise NotImplementedError('get_session_list is not implemented')    # pragma: no cover

    def extract_text(self):
        raise NotImplementedError('extract_text is not implemented')        # pragma: no cover

    def __str__(self):
        return self.name
    __unicode__ = __str__


class JurisdictionScraper(Scraper):
    def scrape(self):
        # yield a single Jurisdiction object
        yield self.jurisdiction

        # if organizations weren't specified yield one top-level org
        if not self.jurisdiction.organizations:
            org = Organization(name=self.jurisdiction.name, classification='legislature')
            org.add_source(self.jurisdiction.url)
            yield org
        else:
            for org in self.jurisdiction.organizations:
                org.add_source(self.jurisdiction.url)
                yield org

        for party in self.jurisdiction.parties:
            org = Organization(classification='party', name=party['name'])
            org.add_source(self.jurisdiction.url)
            yield org

        for post in self.jurisdiction.posts:
            yield post
