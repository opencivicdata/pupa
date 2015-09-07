import pytest
import datetime
from pupa.scrape import Disclosure as ScrapeDisclosure


def disclosure_obj():
    disclosure = ScrapeDisclosure(
        classification="lobbying",
        effective_date=datetime.datetime(2011, 1, 22, 0, 0, 0),
        submitted_date=datetime.datetime(2011, 3, 13, 0, 0, 0),
        timezone="America/New_York"
    )
    disclosure.add_source(
        url='http://www.example.com',
        note='Example Source'
    )
    return disclosure


def test_basic_disclosure():
    e = disclosure_obj()
    e.validate()


def test_disclosure_str():
    # TODO
    d = disclosure_obj()
    assert True


def test_bad_disclosure():
    d = disclosure_obj()
    d.classification = "not a valid classification"

    with pytest.raises(ValueError):
        d.validate()


def test_add_registrant():
    d = disclosure_obj()

    assert d.related_entities == []

    d.add_registrant(
        name="Mr. Test Registrant",
        type="person"
    )

    assert len(d.related_entities) == 1

    registrant = d.related_entities[0]
    assert registrant['entity_type'] == 'person'
    assert registrant['note'] == 'registrant'

    d.validate()


def test_add_authority():
    d = disclosure_obj()

    assert d.related_entities == []

    d.add_authority(
        name="Example Authority",
        type="organization"
    )

    assert len(d.related_entities) == 1

    authority = d.related_entities[0]
    assert authority['entity_type'] == 'organization'
    assert authority['note'] == 'authority'

    d.validate()


def test_add_disclosed_event():
    d = disclosure_obj()

    assert d.related_entities == []

    d.add_disclosed_event(
        name="Example Event",
        type="event"
    )

    assert len(d.related_entities) == 1

    event = d.related_entities[0]
    assert event['entity_type'] == 'event'
    assert event['note'] == 'disclosed_event'

    d.validate()


def test_add_document():
    d = disclosure_obj()
    assert d.documents == []
    d.add_document(note='hello', url='http://example.com', media_type="text/html")
    assert len(d.documents) == 1
    o = d.documents[0]
    assert o['note'] == 'hello'
    assert o['links'] == [{'url': 'http://example.com', 'media_type': 'text/html'}]
    d.validate()
