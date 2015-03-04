from .base import BaseImporter
from opencivicdata.models import (Disclosure,
                                  DisclosureSource,
                                  DisclosureDocument, DisclosureDocumentLink,
                                  DisclosureRelatedEntity,
                                  DisclosureIdentifier,
                                  )
from pupa.exceptions import UnresolvedIdError
from pupa.utils import make_pseudo_id


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
                 event_importer, dedupe_exact=False):
        super(DisclosureImporter, self).__init__(jurisdiction_id,
                                                 dedupe_exact=dedupe_exact)
        self.org_importer = org_importer
        self.person_importer = person_importer
        self.event_importer = event_importer

    def limit_spec(self, spec):
        return spec

    def get_object(self, data):
        spec = {'sources__url': data['sources'][0]['url'],
                'effective_date': data['effective_date'],
                'submitted_date': data['submitted_date']}

        return self.model_class.objects.get(**spec)

    def prepare_for_db(self, data):
        new_related_entities = []

        for entity in data['related_entities']:
            entity_id = entity.pop('id')
            print('looking_up {}'.format(entity_id))
            #if entity['note'] == 'authority':
            #    etype = entity['entity_type']
            #    entity['organization_id'] = self.org_importer.resolve_json_id(entity_id)
            #    print('found {}'.format(entity['organization_id']))
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
                print('found {}'.format(entity['person_id']))
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
                print('found {}'.format(entity['organization_id']))
            elif entity['entity_type'] == 'event':
                try:
                    entity_pseudo_id = make_pseudo_id(
                        sources__url=data['sources'][0]['url'],
                        name=entity['name'],
                    )
                    entity['event_id'] = self.org_importer.resolve_json_id(
                        entity_pseudo_id)
                except UnresolvedIdError:
                    entity['event_id'] = self.event_importer.resolve_json_id(entity_id)
                print('found {}'.format(entity['event_id']))
            new_related_entities.append(entity)

        data['related_entities'] = new_related_entities
        data['jurisdiction_id'] = self.jurisdiction_id

        return data
