import pytest
import datetime
from pupa.scrape import Event


def event_obj():
    e = Event(
        name="get-together",
        start_date=datetime.datetime.utcnow().isoformat().split('.')[0] + 'Z',
        location_name="Joe's Place",
    )
    e.add_source(url='http://example.com/foobar')
    return e


def test_basic_event():
    e = event_obj()
    e.validate()


def test_event_str():
    e = event_obj()
    assert e.name in str(e)


def test_bad_event():
    e = event_obj()
    e.start_date = 6

    with pytest.raises(ValueError):
        e.validate()


def test_basic_agenda():
    e = event_obj()
    agenda = e.add_agenda_item("foo bar")
    assert agenda['description'] == 'foo bar'
    assert e.agenda[0] == agenda
    e.validate()


def test_agenda_add_person():
    e = event_obj()
    agenda = e.add_agenda_item("foo bar")
    assert agenda['related_entities'] == []

    agenda.add_person(person='John Q. Hacker', note='chair')
    assert len(e.agenda[0]['related_entities']) == 1
    e.validate()


def test_agenda_add_vote_event():
    e = event_obj()
    agenda = e.add_agenda_item("foo bar")
    assert agenda['related_entities'] == []

    agenda.add_vote_event(vote_event='Roll no. 12')
    assert len(e.agenda[0]['related_entities']) == 1
    e.validate()


def test_agenda_add_subject():
    e = event_obj()
    agenda = e.add_agenda_item("foo bar")

    agenda.add_subject('test')
    assert e.agenda[0]['subjects'] == ['test']
    agenda.add_subject('test2')
    assert e.agenda[0]['subjects'] == ['test', 'test2']

    e.validate()


def test_agenda_add_classification():
    e = event_obj()
    agenda = e.add_agenda_item("foo bar")

    agenda.add_classification('test')
    assert e.agenda[0]['classification'] == ['test']
    agenda.add_classification('test2')
    assert e.agenda[0]['classification'] == ['test', 'test2']

    e.validate()


def test_agenda_add_extra():
    e = event_obj()
    a = e.add_agenda_item('foo bar')
    a['extras'] = dict(foo=1, bar=['baz'])

    assert e.agenda[0]['extras'] == {'foo': 1, 'bar': ['baz']}


def test_add_committee():
    e = event_obj()
    agenda = e.add_agenda_item("foo bar")
    assert agenda['related_entities'] == []

    agenda.add_committee(committee='Hello, World', note='host')
    e.validate()


def test_add_bill():
    e = event_obj()
    agenda = e.add_agenda_item("foo bar")
    assert agenda['related_entities'] == []
    agenda.add_bill(bill='HB 101', note='consideration')
    e.validate()


def test_add_document():
    e = event_obj()
    assert e.documents == []
    e.add_document(note='hello', url='http://example.com', media_type="text/html")
    assert len(e.documents) == 1
    o = e.documents[0]
    assert o['note'] == 'hello'
    assert o['links'] == [{'url': 'http://example.com', 'media_type': 'text/html', 'text': ''}]
    e.validate()


def test_participants():
    e = event_obj()
    e.add_participant('Committee of the Whole', type='committee', note='everyone')
    assert len(e.participants) == 1
    assert e.participants[0]['name'] == 'Committee of the Whole'
    assert e.participants[0]['entity_type'] == 'committee'
    assert e.participants[0]['note'] == 'everyone'

    # and add_person, which is a shortcut
    e.add_person('Bill Stevenson')
    assert len(e.participants) == 2
    assert e.participants[1]['name'] == 'Bill Stevenson'
    assert e.participants[1]['entity_type'] == 'person'
    assert e.participants[1]['note'] == 'participant'


def test_set_location():
    e = event_obj()
    e.set_location('North Pole', note='it is cold here', url='https://www.northpole.com',
                   coordinates={'latitude': '90.0000', 'longitude': '0.0000'})

    assert e.location.get('name') == 'North Pole'
    assert e.location.get('note') == 'it is cold here'
    assert e.location.get('url') == 'https://www.northpole.com'
    assert e.location.get('coordinates').get('latitude') == '90.0000'
    assert e.location.get('coordinates').get('longitude') == '0.0000'

    e.validate()


def test_add_media():
    e = event_obj()
    name = "Hello, World"
    a = e.add_agenda_item(description='foo')
    a.add_media_link(note=name, url="http://pault.ag", media_type="text/html")
    a.add_media_link(note=name, url="ftp://pault.ag", media_type="text/plain")
    e.validate()
    assert len(e.agenda[0]['media']) == 1
    assert len(e.agenda[0]['media'][0]['links']) == 2

    e.add_media_link(note=name, url="http://pault.ag", media_type="text/html")
    e.add_media_link(note=name, url="ftp://pault.ag", media_type="text/plain")
    e.validate()
    assert len(e.media) == 1
    assert len(e.media[0]['links']) == 2
