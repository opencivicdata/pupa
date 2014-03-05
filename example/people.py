from pupa.scrape import Scraper
from pupa.scrape.helpers import Legislator, Organization


class PersonScraper(Scraper):

    def get_people(self):
        # committee
        tech = Organization('Technology', classification='committee')
        tech.add_post('Chairman', 'chairman')
        tech.add_source('https://example.com')
        yield tech

        # subcommittee
        ecom = Organization('Subcommittee on E-Commerce',
                            parent=tech,
                            classification='committee')
        ecom.add_source('https://example.com')
        yield ecom

        p = Legislator('Paul Tagliamonte', '6')
        p.add_membership(tech, role='chairman')
        p.add_source('https://example.com')
        yield p
