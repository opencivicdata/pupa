from pupa.scrape import Jurisdiction, Scraper
from larvae.person import Person
from larvae.organization import Organization

class Example(Jurisdiction):
    organization_id = 'ex'

    def get_metadata(self):
        return {'name': 'Example',
                'terms': [{'name': '2013-2014', 'sessions': ['2013']}],
                'provides': ['person', 'organization', 'membership'],
                'parties': [{'name': 'Independent', 'id': 'independent'},
                            {'name': 'Green', 'id': 'green'},
                            {'name': 'Bull-Moose', 'id': 'bullmoose'}
                           ],
                'id': self.organization_id
               }

    def get_scraper(self, term, session, obj_type):
        if obj_type == 'person':
            return ExamplePersonScraper

    def get_session_list(self):
        return ['1999', '2000']


class Legislator(Person):
    _type = 'legislator'
    __slots__ = ('district', 'party', 'chamber', '_contact_details')

    def __init__(self, name, district, party=None, chamber=None, **kwargs):
        super(Legislator, self).__init__(name, **kwargs)
        self.district = district
        self.party = party
        self.chamber = chamber
        self._contact_details = []

    def add_contact(self, type, value, group):
        self._contact_details.append({'type': type, 'value': value,
                                      'group': group})

    def add_committee_membership(self, com_name):
        org = Organization(com_name, classification='committee')
        self.add_membership(org)
        self._related.append(org)


class ExamplePersonScraper(Scraper):

    def get_people(self):
        tech = Organization('Technology', classification='committee')
        tech.add_post('Chairman', 'chairman')
        yield tech

        p = Legislator('Paul Tagliamonte', district='6', chamber='upper',
                       party='Independent')
        p.add_committee_membership('Finance')
        p.add_membership(tech)
        yield p
