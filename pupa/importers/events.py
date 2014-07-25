import pytz
import datetime

from .base import BaseImporter
from ..utils.event import read_event_iso_8601
from opencivicdata.models import (Event, EventLocation, EventSource, EventDocument,
                                  EventDocumentLink, EventLink, EventParticipant, EventMedia,
                                  EventMediaLink, EventAgendaItem, EventRelatedEntity,
                                  EventAgendaMedia, EventAgendaMediaLink)


class EventImporter(BaseImporter):
    _type = 'event'
    model_class = Event
    related_models = {
        'sources': (EventSource, 'event_id', {}),
        'documents': (EventDocument, 'event_id', {
            'links': (EventDocumentLink, 'document_id', {})
        }),
        'links': (EventLink, 'event_id', {}),
        'participants': (EventParticipant, 'event_id', {}),
        'media': (EventMedia, 'event_id', {
            'links': (EventMediaLink, 'media_id', {}),
        }),
        'agenda': (EventAgendaItem, 'event_id', {
            'related_entities': (EventRelatedEntity, 'agenda_item_id', {}),
            'media': (EventAgendaMedia, 'agenda_item_id', {
                'links': (EventAgendaMediaLink, 'media_id', {}),
            }),
        })
    }
    preserve_order = ('agenda',)

    def get_object(self, event):
        spec = {
            'name': event['name'],
            'description': event['description']
            'start_time': event['start_time'],
            'end_time': event['end_time'],
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
