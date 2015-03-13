from .base import BaseImporter
from django.db.models import Q

from opencivicdata.models import (Disclosure,
                                  DisclosureSource,
                                  DisclosureDocument, DisclosureDocumentLink,
                                  DisclosureRelatedEntity,
                                  DisclosureIdentifier,
                                  )
from pupa.exceptions import UnresolvedIdError
from ..utils import make_pseudo_id
from ..utils.event import read_event_iso_8601


class DisclosureImporter(BaseImporter):
    _type = 'disclosure'
    model_class = Disclosure
    related_models = {
        'sources': (DisclosureSource, 'disclosure_id', {}),
        'documents': (DisclosureDocument, 'disclosure_id', {
            'links': (DisclosureDocumentLink, 'document_id', {})
        }),
        'related_entities': (DisclosureRelatedEntity, 'disclosure_id', {}),
        'identifiers': (DisclosureIdentifier, 'disclosure_id', {})
    }

    def __init__(self, jurisdiction_id, org_importer, person_importer,
                 event_importer):
        super(DisclosureImporter, self).__init__(jurisdiction_id)
        self.org_importer = org_importer
        self.person_importer = person_importer
        self.event_importer = event_importer

    def limit_spec(self, spec):
        return spec

    def get_object(self, data):
        spec = {'effective_date': data['effective_date'],
                'submitted_date': data['submitted_date']}
        
        main_query = Q(**spec)

        if data['source_identified']:
            source_qs = []
            if len(data['sources']) == 0:
                raise KeyError('source-identified disclosure {} has no sources!'.format(
                    data['name']))
            for s in data['sources']:
                sq = {}
                sq['sources__url'] = s['url']
                sq['sources__note'] = s.get('note', '')
                source_qs.append(Q(**sq))
            source_query = source_qs.pop()
            for q in source_qs:
                source_query |= q
            main_query &= source_query

        return self.model_class.objects.get(main_query)

        return self.model_class.objects.get(**spec)

    def prepare_for_db(self, data):
        gdt = lambda x: read_event_iso_8601(x) if x is not None else None

        data['submitted_date'] = gdt(data.get('submitted_date', None))
        data['effective_date'] = gdt(data.get('effective_date', None))

        new_related_entities = []

        for entity in data['related_entities']:
            entity_id = entity.pop('id')
            if entity['entity_type'] == 'person':
                try:
                    entity_pseudo_id = make_pseudo_id(
                        sources__url=data['sources'][0]['url'],
                        name=entity['name'],
                    )

                    entity['person_id'] = self.person_importer.resolve_json_id(
                        entity_pseudo_id)
                except UnresolvedIdError:
                    entity['person_id'] = self.person_importer.resolve_json_id(entity_id)
            elif entity['entity_type'] == 'organization':
                try:
                    entity_pseudo_id = make_pseudo_id(
                        sources__url=data['sources'][0]['url'],
                        name=entity['name'],
                    )
                    entity['organization_id'] = self.org_importer.resolve_json_id(
                        entity_pseudo_id)
                except UnresolvedIdError:
                    entity['organization_id'] = self.org_importer.resolve_json_id(entity_id)
            elif entity['entity_type'] == 'event':
                try:
                    entity_pseudo_id = make_pseudo_id(
                        sources__url=data['sources'][0]['url'],
                        name=entity['name'],
                    )
                    entity['event_id'] = self.event_importer.resolve_json_id(
                        entity_pseudo_id)
                except UnresolvedIdError:
                    entity['event_id'] = self.event_importer.resolve_json_id(entity_id)
            new_related_entities.append(entity)

        data['related_entities'] = new_related_entities
        data['jurisdiction_id'] = self.jurisdiction_id

        return data
