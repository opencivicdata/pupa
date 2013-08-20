from pupa.scrape import Scraper
from pupa.models.organization import Legislator, Organization


class PersonScraper(Scraper):

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
