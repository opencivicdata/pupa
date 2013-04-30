from pupa.scrape import Jurisdiction, Scraper
from larvae.person import Person
from larvae.organization import Organization


class Example(Jurisdiction):
    jurisdiction_id = 'ex'

    def get_metadata(self):
        return {'name': 'Example',
                'legislature_name': 'Example Legislature',
                'legislature_url': 'http://example.com',
                'terms': [{'name': '2013-2014', 'sessions': ['2013'],
                           'start_year': 2013, 'end_year': 2014
                          }],
                'provides': ['person'],
                'parties': [{'name': 'Independent' },
                            {'name': 'Green' },
                            {'name': 'Bull-Moose'}
                           ],
                'session_details': {'2013': {'_scraped_name': '2013'}},
                'feature_flags': [],
               }

    def get_scraper(self, term, session, scraper_type):
        if scraper_type == 'person':
            return ExamplePersonScraper

    def scrape_session_list(self):
        return ['2013']


class Legislator(Person):
    _type = 'person'
    _is_legislator = True
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

    def add_committee_membership(self, com_name, role='member'):
        org = Organization(com_name, classification='committee')
        self.add_membership(org, role=role)
        self._related.append(org)


class ExamplePersonScraper(Scraper):

    def get_people(self):
        # committee
        tech = Organization('Technology', classification='committee')
        tech.add_post('Chairman', 'chairman')
        yield tech

        # subcommittee
        ecom = Organization('Subcommittee on E-Commerce',
                            parent=tech,
                            classification='committee')
        yield ecom

        p = Legislator('Paul Tagliamonte', district='6', chamber='upper',
                       party='Independent')
        p.add_committee_membership('Finance')
        p.add_membership(tech, role='chairman')
        yield p
