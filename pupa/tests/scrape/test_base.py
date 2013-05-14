import mock
from nose.tools import assert_equal, assert_in, assert_raises

from larvae.person import Person
from larvae.organization import Organization
from pupa.scrape.base import Scraper


def test_save_object_basics():
    s = Scraper('jurisdiction', '2013', '/tmp/')
    p = Person('Michael Jordan')

    with mock.patch('json.dump') as json_dump:
        s.save_object(p)

    # saved in right place
    filename = 'person_' + p._id + '.json'
    assert_in(filename, s.output_names['person'])
    json_dump.assert_called_once_with(p.as_dict(), mock.ANY, cls=mock.ANY)


def test_save_invalid_object():
    s = Scraper('jurisdiction', '2013', '/tmp/')
    p = Person('Michael Jordan')

    # this is hideous...
    with assert_raises(ValueError):
        with mock.patch.object(Person, 'as_dict', new=lambda s: {'bad': 'x'}):
            s.save_object(p)


def test_save_related():
    s = Scraper('jurisdiction', '2013', '/tmp/')
    p = Person('Michael Jordan')
    o = Organization('Chicago Bulls')
    p._related.append(o)

    with mock.patch('json.dump') as json_dump:
        s.save_object(p)

    assert_equal(json_dump.mock_calls, [
        mock.call(p.as_dict(), mock.ANY, cls=mock.ANY),
        mock.call(o.as_dict(), mock.ANY, cls=mock.ANY)
    ])


def test_save_legislator():
    pass
