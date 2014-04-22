import pytest
import datetime
from pupa.scrape import Event


def event_obj():
    e = Event(name="get-together", when=datetime.datetime.utcnow(), location="Joe's Place")
    e.add_source(url='foobar')
    return e


def test_basic_event():
    e = event_obj()
    e.validate()


def test_bad_event():
    e = event_obj()
    e.when = 6

    with pytest.raises(ValueError):
        e.validate()


def test_add_link():
    e = event_obj()
    e.add_link("http://foobar.baz")
    e.add_link("http://foobar.baz", note="foo")
    assert len(e.links) == 2
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
    e.add_document(name='hello', url='http://example.com', mimetype="text/html")
    assert len(e.documents) == 1
    o = e.documents[0]
    assert o['name'] == 'hello'
    assert o['links'] == [{'url': 'http://example.com', 'mimetype': 'text/html'}]
    e.validate()


def test_add_media():
    e = event_obj()
    name = "Hello, World"
    a = e.add_agenda_item(description='foo')
    a.add_media_link(name=name, url="http://pault.ag", type='media', mimetype="text/html")
    a.add_media_link(name=name, url="ftp://pault.ag", type='media', mimetype="text/plain")
    e.validate()
    assert len(e.agenda[0]['media']) == 1
    assert len(e.agenda[0]['media'][0]['links']) == 2

    e.add_media_link(name=name, url="http://pault.ag", type='media', mimetype="text/html")
    e.add_media_link(name=name, url="ftp://pault.ag", type='media', mimetype="text/plain")
    e.validate()
    assert len(e.media) == 1
    assert len(e.media[0]['links']) == 2
