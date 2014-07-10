import pytz
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

        # Now. We'll take in the POSIX timestamp (set to UTC) and timezone
        # qualify it back to localtime.
        timezone = data.pop('timezone')
        # We pop off the timezone, since this is used to send the timezone
        # qualified datetime to the importer. The database is timezone aware,
        # so there's no need to store it in the database.

        gdt = lambda x: datetime.datetime.fromtimestamp(
            x, pytz.timezone(timezone)) if x is not None else None

        # Now, set them back to the object, to prepare them for DB.
        data['start_time'] = gdt(data['start_time'])
        data['end_time'] = gdt(data.get('end_time', None))

        return data
