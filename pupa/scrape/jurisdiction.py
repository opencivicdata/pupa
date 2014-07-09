from .base import BaseModel, Scraper
from .schemas.jurisdiction import schema
from .popolo import Organization


class Jurisdiction(BaseModel):
    """ Base class for a jurisdiction """

    _type = 'jurisdiction'
    _schema = schema

    # schema objects
    classification = None
    name = None
    url = None
    legislative_sessions = []
    feature_flags = []
    extras = {}
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

    def __init__(self):
        super(BaseModel, self).__init__()
        self._related = []
        self._meta = {}
        self.extras = {}

    @property
    def jurisdiction_id(self):
        return '{}/{}'.format(self.division_id.replace('ocd-division', 'ocd-jurisdiction'),
                              self.classification)

    _id = jurisdiction_id

    def as_dict(self):
        return {'_id': self.jurisdiction_id, 'id': self.jurisdiction_id,
                'name': self.name, 'url': self.url, 'division_id': self.division_id,
                'classification': self.classification,
                'legislative_sessions': self.legislative_sessions,
                'feature_flags': self.feature_flags, 'extras': self.extras, }

    def get_session_list(self):
        raise NotImplementedError('get_session_list is not implemented')    # pragma: no cover

    def extract_text(self):
        raise NotImplementedError('extract_text is not implemented')        # pragma: no cover

    def __str__(self):
        return self.name


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
