import mock
import pytest
from pupa.scrape import Person, Organization, Bill, Jurisdiction
from pupa.scrape.base import Scraper, ScrapeError, BaseBillScraper


class FakeJurisdiction(Jurisdiction):
    jurisdiction_id = 'jurisdiction'


juris = FakeJurisdiction()


def test_save_object_basics():
    # ensure that save object dumps a file
    s = Scraper(juris, '/tmp/')
    p = Person('Michael Jordan')
    p.add_source('http://example.com')

    with mock.patch('json.dump') as json_dump:
        s.save_object(p)

    # ensure object is saved in right place
    filename = 'person_' + p._id + '.json'
    assert filename in s.output_names['person']
    json_dump.assert_called_once_with(p.as_dict(), mock.ANY, cls=mock.ANY)


def test_save_object_invalid():
    s = Scraper(juris, '/tmp/')
    p = Person('Michael Jordan')
    # no source, won't validate

    with pytest.raises(ValueError):
        s.save_object(p)


def test_save_related():
    s = Scraper(juris, '/tmp/')
    p = Person('Michael Jordan')
    p.add_source('http://example.com')
    o = Organization('Chicago Bulls', classification='committee')
    o.add_source('http://example.com')
    p._related.append(o)

    with mock.patch('json.dump') as json_dump:
        s.save_object(p)

    assert json_dump.mock_calls == [mock.call(p.as_dict(), mock.ANY, cls=mock.ANY),
                                    mock.call(o.as_dict(), mock.ANY, cls=mock.ANY)]


def test_simple_scrape():
    class FakeScraper(Scraper):
        def scrape(self):
            p = Person('Michael Jordan')
            p.add_source('http://example.com')
            yield p

    with mock.patch('json.dump') as json_dump:
        record = FakeScraper(juris, '/tmp/').do_scrape()

    assert len(json_dump.mock_calls) == 1
    assert record['objects']['person'] == 1
    assert record['end'] > record['start']
    assert record['skipped'] == 0


def test_double_iter():
    """ tests that scrapers that yield iterables work OK """
    class IterScraper(Scraper):
        def scrape(self):
            yield self.scrape_people()

        def scrape_people(self):
            p = Person('Michael Jordan')
            p.add_source('http://example.com')
            yield p

    with mock.patch('json.dump') as json_dump:
        record = IterScraper(juris, '/tmp/').do_scrape()

    assert len(json_dump.mock_calls) == 1
    assert record['objects']['person'] == 1


def test_no_objects():
    class NullScraper(Scraper):
        def scrape(self):
            pass

    with pytest.raises(ScrapeError):
        NullScraper(juris, '/tmp/', fastmode=True).do_scrape()


def test_no_scrape():
    class NonScraper(Scraper):
        pass

    with pytest.raises(NotImplementedError):
        NonScraper(juris, '/tmp/').do_scrape()


def test_bill_scraper():
    class BillScraper(BaseBillScraper):
        def get_bill_ids(self):
            yield '1', {'extra': 'param'}
            yield '2', {}

        def get_bill(self, bill_id, **kwargs):
            if bill_id == '1':
                assert kwargs == {'extra': 'param'}
                raise self.ContinueScraping
            else:
                assert bill_id == '2'
                assert kwargs == {}
                b = Bill('1', self.legislative_session, 'title')
                b.add_source('http://example.com')
                return b

    bs = BillScraper(juris, '/tmp/')
    with mock.patch('json.dump') as json_dump:
        record = bs.do_scrape(legislative_session='2020')

    assert len(json_dump.mock_calls) == 1
    assert record['objects']['bill'] == 1
    assert record['skipped'] == 1
