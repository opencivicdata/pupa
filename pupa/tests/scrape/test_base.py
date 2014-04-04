import mock
from nose.tools import assert_equal, assert_in, assert_raises

from pupa.models.person import Person
from pupa.models.organization import Organization
from pupa.scrape.base import Scraper


def test_save_object_basics():
    s = Scraper('jurisdiction', '/tmp/')
    p = Person('Michael Jordan')
    p.add_source('http://example.com')

    with mock.patch('json.dump') as json_dump:
        s.save_object(p)

    # saved in right place
    filename = 'person_' + p._id + '.json'
    assert_in(filename, s.output_names['person'])
    json_dump.assert_called_once_with(p.as_dict(), mock.ANY, cls=mock.ANY)


def test_save_invalid_object():
    s = Scraper('jurisdiction', '/tmp/')
    p = Person('Michael Jordan')
    # no source, won't validate

    with assert_raises(ValueError):
        s.save_object(p)


def test_save_related():
    s = Scraper('jurisdiction', '/tmp/')
    p = Person('Michael Jordan')
    p.add_source('http://example.com')
    o = Organization('Chicago Bulls')
    o.add_source('http://example.com')
    p._related.append(o)

    with mock.patch('json.dump') as json_dump:
        s.save_object(p)

    assert_equal(json_dump.mock_calls, [
        mock.call(p.as_dict(), mock.ANY, cls=mock.ANY),
        mock.call(o.as_dict(), mock.ANY, cls=mock.ANY)
    ])
