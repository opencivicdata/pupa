from pupa.models import Event
import datetime as dt


def event_obj():
    e = Event(name="get-together",
              when=dt.datetime.utcnow(),
              location="Joe's Place")

    e.add_source(url='foobar')
    e.validate()
    return e


def test_basic_event():
    """ test that we can create an event """
    e = Event(name="get-together",
              when=dt.datetime.utcnow(),
              location="Joe's Place")

    e.add_source(url='foobar')
    e.validate()

    e.add_link("http://foobar.baz")
    e.add_link("http://foobar.baz", note="foo")
    e.validate()

    assert len(e.links) == 2


def test_basic_agenda():
    e = Event(name="get-together",
              when=dt.datetime.utcnow(),
              location="Joe's Place")

    e.add_source(url='foobar')
    e.validate()

    agenda = e.add_agenda_item("foo bar")
    assert agenda
    e.validate()


def test_add_person():
    e = event_obj()
    agenda = e.add_agenda_item("foo bar")
    assert agenda['related_entities'] == []

    agenda.add_person(person='John Q. Hacker', note='chair')
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
    e.add_document(name='hello', url='http://example.com',
                   mimetype="text/html")
    assert len(e.documents) == 1
    o = e.documents[0]
    assert o['name'] == 'hello'
    assert o['url'] == 'http://example.com'
    e.validate()


def test_add_media():
    e = event_obj()
    e.validate()
    name = "Hello, World"

    a = e.add_agenda_item(description='foo')

    a.add_media_link(name=name, url="http://pault.ag", type='media',
                     mimetype="text/html")

    a.add_media_link(name=name, url="ftp://pault.ag",
                     type='media', mimetype="text/ftp-or-something")

    e.validate()

    assert len(e.agenda[0]['media']) == 1
    assert len(e.agenda[0]['media'][0]['links']) == 2

    e.add_media_link(name=name, url="http://pault.ag", type='media',
                     mimetype="text/html")

    e.add_media_link(name=name, url="ftp://pault.ag",
                     type='media', mimetype="text/ftp-or-something")

    e.validate()

    assert len(e.media) == 1
    assert len(e.media[0]['links']) == 2
