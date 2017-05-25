from .base import BaseImporter
from pupa.utils import fix_bill_id, get_pseudo_id, _make_pseudo_id
from pupa.utils.event import read_event_iso_8601
from opencivicdata.legislative.models import (Event, EventLocation, EventSource, EventDocument,
                                              EventDocumentLink, EventLink, EventParticipant,
                                              EventMedia, EventMediaLink, EventAgendaItem,
                                              EventRelatedEntity, EventAgendaMedia,
                                              EventAgendaMediaLink)


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

    def __init__(self, jurisdiction_id, org_importer, person_importer, bill_importer,
                 vote_event_importer):
        super(EventImporter, self).__init__(jurisdiction_id)
        self.org_importer = org_importer
        self.person_importer = person_importer
        self.bill_importer = bill_importer
        self.vote_event_importer = vote_event_importer

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

        def gdt(x):
            if x is not None:
                return read_event_iso_8601(x)

        data['start_time'] = gdt(data['start_time'])
        data['end_time'] = gdt(data.get('end_time', None))

        for participant in data['participants']:
            if 'person_id' in participant:
                participant['person_id'] = self.person_importer.resolve_json_id(
                    participant['person_id'],
                    allow_no_match=True)
            elif 'organization_id' in participant:
                participant['organization_id'] = self.org_importer.resolve_json_id(
                    participant['organization_id'],
                    allow_no_match=True)

        for item in data['agenda']:
            for entity in item['related_entities']:
                if 'person_id' in entity:
                    entity['person_id'] = self.person_importer.resolve_json_id(
                        entity['person_id'],
                        allow_no_match=True)
                elif 'organization_id' in entity:
                    entity['organization_id'] = self.org_importer.resolve_json_id(
                        entity['organization_id'],
                        allow_no_match=True)
                elif 'bill_id' in entity:
                    bill = get_pseudo_id(entity['bill_id'])
                    bill['identifier'] = fix_bill_id(bill['identifier'])
                    bill = _make_pseudo_id(**bill)
                    entity['bill_id'] = self.bill_importer.resolve_json_id(
                        bill,
                        allow_no_match=True)
                elif 'vote_event_id' in entity:
                    entity['vote_event_id'] = self.vote_event_importer.resolve_json_id(
                        entity['vote_event_id'],
                        allow_no_match=True)

        return data
