from larvae.organization import Organization

class Jurisdiction(object):
    """ Base class for a jurisdiction """

    _metadata = None
    _party_cache = {}

    @property
    def metadata(self):
        if not self._metadata:
            self._metadata = self.get_metadata()
        return self._metadata

    def term_for_session(self, session):
        for term in self.metadata['terms']:
            if session in term['sessions']:
                return term['name']
        raise ValueError('no such session: ' + session)

    def get_term_details(self, termname):
        for term in self.metadata['terms']:
            if term['name'] == termname:
                return term
        raise ValueError('no such term: ' + termname)

    def get_party(self, party_name):
        if not self._party_cache:
            for party in self.metadata['parties']:
                self._party_cache[party['name']] = Organization(party['name'],
                                                            _id=party['id'])
        try:
            return self._party_cache[party_name]
        except KeyError:
            raise ValueError('no such party: ' + party_name)

    def get_metadata(self):
        raise NotImplementedError('get_metadata method is not implemented')

    def get_session_list(self):
        raise NotImplementedError('get_session_list is not implemented')

    def extract_text(self):
        raise NotImplementedError('extract_text is not implemented')

    def get_scraper(self, term, session, obj_type):
        raise NotImplementedError('get_scraper is not implemented')
