import pytz
import datetime

from .base import BaseImporter
from ..utils.event import read_event_iso_8601
from opencivicdata.models import Event, EventLocation


class EventImporter(BaseImporter):
    _type = 'event'
    model_class = Event
    related_models = {'sources': {},  'documents': {'links': {}}, 'links': {}, 'participants': {},
                      'media': {'links': {}},
                      'agenda': {'related_entities': {}, 'media': {}, 'links': {}}}
    preserve_order = {'agenda'}

    def get_object(self, event):
        spec = {
            'name': event['name'],
            'start_time': event['start_time'],
            'timezone': event['timezone'],
            'jurisdiction_id': self.jurisdiction_id
        }
        return self.model_class.objects.get(**spec)


    def get_location(self, location_data):
        obj, created = EventLocation.objects.get_or_create(name=location_data['name'],
                                                           url=location_data.get('url', ''),
                                                           jurisdiction_id=self.jurisdiction_id)
        # TODO: geocode here?
        return obj

    def prepare_for_db(self, data):
        data['jurisdiction_id'] = self.jurisdiction_id
        data['location'] = self.get_location(data['location'])

        gdt = lambda x: read_event_iso_8601(x) if x is not None else None

        data['start_time'] = gdt(data['start_time'])
        data['end_time'] = gdt(data.get('end_time', None))

        return data
