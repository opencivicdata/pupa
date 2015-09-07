from .base import BaseImporter
from ..utils.event import read_event_iso_8601
from opencivicdata.models import (Event, EventLocation, EventSource, EventDocument,
                                  EventDocumentLink, EventLink, EventParticipant, EventMedia,
                                  EventMediaLink, EventAgendaItem, EventRelatedEntity,
                                  EventAgendaMedia, EventAgendaMediaLink)
from pupa.exceptions import UnresolvedIdError
from pupa.utils import make_pseudo_id


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
    
    def __init__(self, jurisdiction_id, org_importer, person_importer):
        super(EventImporter, self).__init__(jurisdiction_id)
        self.org_importer = org_importer
        self.person_importer = person_importer
    
    def limit_spec(self, spec):
        return spec

    def get_object(self, event):
        spec = {
            'name': event['name'],
            'description': event['description'],
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
       
        resolved_participants = []

        for entity in data['participants']:
            entity_id = entity.pop('id', None)
            if entity['entity_type'] == 'person':
                try:
                    entity_pseudo_id = make_pseudo_id(
                        sources__url=data['sources'][0]['url'],
                        name=entity['name'],
                    )
                    
                    entity['person_id'] = self.person_importer.resolve_json_id(
                        entity_pseudo_id)
                except (UnresolvedIdError, KeyError, IndexError):
                    entity['person_id'] = self.person_importer.resolve_json_id(entity_id)
            elif entity['entity_type'] == 'organization':
                try:
                    entity_pseudo_id = make_pseudo_id(
                        sources__url=data['sources'][0]['url'],
                        name=entity['name'],
                    )
                    entity['organization_id'] = self.org_importer.resolve_json_id(
                        entity_pseudo_id)
                except (UnresolvedIdError, KeyError, IndexError):
                    entity['organization_id'] = self.org_importer.resolve_json_id(entity_id)
            resolved_participants.append(entity)

        data['participants'] = resolved_participants

        return data
