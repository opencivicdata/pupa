from pupa.scrape import Organization, Scraper
from larvae.person import Person

class Example(Organization):
    organization_id = 'ex'

    def get_metadata(self):
        return {'name': 'Example',
                'terms': [{'name': '2013-2014', 'sessions': ['2013']}],
                'provides': ['person'],
                'id': self.organization_id
               }

    def get_scraper(self, term, session, obj_type):
        if obj_type == 'person':
            return ExamplePersonScraper

    def get_session_list(self):
        return ['1999', '2000']

class ExamplePersonScraper(Scraper):
    def get_people(self):

        yield Person('Paul Tagliamonte')
        yield Person('Thom Neale')
        yield Person('James Turk')
