import pytest
import datetime as dt
from pupa.scrape import Event as ScrapeEvent
from pupa.importers import EventImporter
from opencivicdata.models import Event, Jurisdiction


def ge():
    event = ScrapeEvent(
        name="America's Birthday",
        start_time="2014-07-04T05:00Z",
        location="America",
        timezone="America/New_York",
        all_day=True)
    event.add_person("George Washington")
    return event


@pytest.mark.django_db
def test_related_people_event():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_person(person="John Q. Public")

    result = EventImporter('jid').import_data([event1.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid').import_data([event2.as_dict()])
    assert result['event']['noop'] == 1


@pytest.mark.django_db
def test_related_bill_event():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_bill(bill="HB 101")

    result = EventImporter('jid').import_data([event1.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid').import_data([event2.as_dict()])
    assert result['event']['noop'] == 1


@pytest.mark.django_db
def test_related_committee_event():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_committee(committee="Fiscal Committee")

    result = EventImporter('jid').import_data([event1.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid').import_data([event2.as_dict()])
    assert result['event']['noop'] == 1


@pytest.mark.django_db
def test_media_event():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        item = event.add_agenda_item("Cookies will be served")
        item.add_media_link(
            note="Hello, World",
            media_type='application/octet-stream',
            url="http://hello.world/foo"
        )

    result = EventImporter('jid').import_data([event1.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid').import_data([event2.as_dict()])
    assert result['event']['noop'] == 1


@pytest.mark.django_db
def test_media_event():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    event1 = ge()
    event2 = ge()

    for event in [event1, event2]:
        event.add_document(note="Presentation",
                           url="http://example.com/presentation.pdf")

    result = EventImporter('jid').import_data([event1.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid').import_data([event2.as_dict()])
    assert result['event']['noop'] == 1


@pytest.mark.django_db
def test_full_event():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    event = ge()

    result = EventImporter('jid').import_data([event.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid').import_data([event.as_dict()])
    assert result['event']['noop'] == 1

    event = ge()
    event.location['name'] = "United States of America"
    result = EventImporter('jid').import_data([event.as_dict()])
    assert result['event']['update'] == 1


@pytest.mark.django_db
def test_bad_event_time():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    event = ge()
    event.start_time="2014-07-04T05:00"
    pytest.raises(
        ValueError,
        EventImporter('jid').import_item,
        event.as_dict()
    )


@pytest.mark.django_db
def test_top_level_media_event():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    event1, event2 = ge(), ge()

    event1.add_media_link("fireworks", "http://example.com/fireworks.mov",
                          media_type='application/octet-stream')
    event2.add_media_link("fireworks", "http://example.com/fireworks.mov",
                          media_type='application/octet-stream')

    result = EventImporter('jid').import_data([event1.as_dict()])
    assert result['event']['insert'] == 1

    result = EventImporter('jid').import_data([event2.as_dict()])
    assert result['event']['noop'] == 1
