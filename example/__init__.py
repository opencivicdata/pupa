from pupa.scrape import Jurisdiction, Scraper
from larvae.person import Person
from larvae.organization import Organization

class Example(Jurisdiction):
    organization_id = 'ex'

    def get_metadata(self):
        return {'name': 'Example',
                'terms': [{'name': '2013-2014', 'sessions': ['2013']}],
                'provides': ['person', 'organization', 'membership'],
                'id': self.organization_id
               }

    def get_scraper(self, term, session, obj_type):
        if obj_type == 'person':
            return ExamplePersonScraper

    def get_session_list(self):
        return ['1999', '2000']


class Legislator(Person):
    __slots__ = ('district', 'party', 'chamber')

    def __init__(self, name, district, party=None, chamber=None, **kwargs):
        super(Legislator, self).__init__(name, **kwargs)
        self.district = district
        self.party = party
        self.chamber = chamber


class ExamplePersonScraper(Scraper):

    def get_people(self):
        tech = Organization('Technology')
        tech.add_post('chairman-dlkfjdlkfjaslf', 'Chairman', 'chairman')

        p = Legislator('Paul Tagliamonte', district='6', chamber='upper',
                       party='I')
        p.add_membership('Finance')
        p.add_membership('Technology')
        yield [tech, p]

        p = Legislator('Thom Neale', district='1', chamber='upper', party='G')
        p.add_membership('Law')
        p.add_membership(tech)
        yield p

        p = Legislator('James Turk', district='2', chamber='lower', party='B')
        m = p.add_membership(tech, post_id='chairman')
        m.contact_details.append({'key': 'phone', 'value': '202-558-8723'})
        p.add_membership('Law')
        yield p
