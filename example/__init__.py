from pupa.scrape import Jurisdiction

from .people import PersonScraper


class Example(Jurisdiction):
    jurisdiction_id = 'ocd-jurisdiction/country:us/state:ex/place:example'
    name = 'Example Legislature'
    url = 'http://example.com'
    provides = ['people']
    parties = [
        {'name': 'Independent' },
        {'name': 'Green' },
        {'name': 'Bull-Moose'}
    ]
    session_details = {
        '2013': {'_scraped_name': '2013'}
    }

    def get_scraper(self, session, scraper_type):
        if scraper_type == 'people':
            return PersonScraper

    def scrape_session_list(self):
        return ['2013']

