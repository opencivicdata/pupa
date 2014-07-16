import pytest
import datetime as dt
from pupa.scrape import Event as ScrapeEvent
from pupa.importers import EventImporter
from opencivicdata.models import Event, Jurisdiction


@pytest.mark.django_db
def test_full_event():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    event = ScrapeEvent(
        name="America's Birthday",
        start_time="2014-07-04T05:00Z",
        location="America",
        timezone="America/New_York",
        all_day=True)
    event.add_person("George Washington")
    event.add_media_link("fireworks", "http://example.com/fireworks.mov")
    ret = EventImporter('jid').import_data([event.as_dict()])
    assert ret['event']['insert'] == 1

    event = ScrapeEvent(
        name="America's Birthday",
        start_time="2014-07-04T05:00Z",
        location="America",
        timezone="America/New_York",
        all_day=True)
    event.add_person("George Washington")
    event.add_media_link("fireworks", "http://example.com/fireworks.mov")
    ret = EventImporter('jid').import_data([event.as_dict()])
    assert ret['event']['noop'] == 1

    event = ScrapeEvent(
        name="America's Birthday",
        start_time="2014-07-04T05:00Z",
        location="United States of America",
        timezone="America/New_York",
        all_day=True)
    event.add_person("George Washington")
    event.add_media_link("fireworks", "http://example.com/fireworks.mov")
    ret = EventImporter('jid').import_data([event.as_dict()])
    assert ret['event']['update'] == 1


@pytest.mark.django_db
def test_bad_event_time():
    j = Jurisdiction.objects.create(id='jid', division_id='did')
    event = ScrapeEvent(
        name="America's Birthday",
        start_time="2014-07-04T05:00",
        location="America",
        timezone="America/New_York",
        all_day=True)
    event.add_person("George Washington")
    event.add_media_link("fireworks", "http://example.com/fireworks.mov")

    pytest.raises(
        ValueError,
        EventImporter('jid').import_data,
        [event.as_dict()]
    )
