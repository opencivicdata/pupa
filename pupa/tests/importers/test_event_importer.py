import pytest
import datetime as dt
from pupa.scrape import Event as ScrapeEvent
from pupa.importers import EventImporter
from opencivicdata.models import Event, Jurisdiction


class DumbMockImporter(object):
    """ this is a mock importer that implements a resolve_json_id that is just a pass-through """

    def resolve_json_id(self, json_id):
        return json_id


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

    EventImporter('jid').import_data([event.as_dict()])


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
