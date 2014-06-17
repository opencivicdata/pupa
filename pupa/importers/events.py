import datetime
from .base import BaseImporter
from opencivicdata.models import Event, EventLocation


class EventImporter(BaseImporter):
    _type = 'event'
    model_class = Event
    related_models = {'sources': {}, 'documents': {}, 'links': {}, 'participants': {},
                      'media': {'links': {}},
                      'agenda': {'related_entities': {}, 'media': {}, 'links': {}}}

    def get_object(self, event):
        spec = {
            'name': event['name'],
            'start_time': event['start_time'],
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
        return data
