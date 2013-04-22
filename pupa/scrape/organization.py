

class Organization(object):
    """ Base class for organizations """

    _metadata = None

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
        raise ValueError('no such term: ' + term)

    def get_metadata(self):
        raise NotImplementedError('get_metadata method is not implemented')

    def get_session_list(self):
        raise NotImplementedError('get_session_list is not implemented')

    def extract_text(self):
        raise NotImplementedError('extract_text is not implemented')

    def get_scraper(self, term, session, obj_type):
        raise NotImplementedError('get_scraper is not implemented')
