from pupa.models.organization import Organization


class Jurisdiction(object):
    """ Base class for a jurisdiction """

    # schema objects
    name = None
    url = None
    chambers = {}
    terms = None
    session_details = None
    feature_flags = []
    building_maps = []
    provides = []
    parties = []
    other_names = []
    parent_id = None
    _ignored_scraped_sessions = []

    _party_cache = {}

    def get_db_object(self):
        return {'name': self.name,
                'url': self.url,
                'chambers': self.chambers,
                'terms': self.terms,
                'session_details': self.session_details,
                'feature_flags': self.feature_flags,
                'building_maps': self.building_maps}

    def term_for_session(self, session):
        for term in self.terms:
            if session in term['sessions']:
                return term['name']
        raise ValueError('no such session: ' + session)

    def get_term_details(self, termname):
        for term in self.terms:
            if term['name'] == termname:
                return term
        raise ValueError('no such term: ' + termname)

    def get_party(self, party_name):
        if not self._party_cache:
            for party in self.parties:
                self._party_cache[party['name']] = Organization(
                    party['name'], _id=party['id'])
        try:
            return self._party_cache[party_name]
        except KeyError:
            raise ValueError('no such party: ' + party_name)

    def get_session_list(self):
        raise NotImplementedError('get_session_list is not implemented')

    def extract_text(self):
        raise NotImplementedError('extract_text is not implemented')

    def get_scraper(self, term, session, obj_type):
        raise NotImplementedError('get_scraper is not implemented')
