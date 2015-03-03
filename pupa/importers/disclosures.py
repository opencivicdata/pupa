from .base import BaseImporter
from opencivicdata.models import (Disclosure,
                                  DisclosureSource,
                                  DisclosureDocument, DisclosureDocumentLink,
                                  DisclosureRelatedEntity,
                                  DisclosureIdentifier,
                                  )


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

    def prepare_for_db(self, data):
        new_related_entities = []
        # prepare registrant
        registrants = [re for re in data['related_entities']
                       if re['note'] == 'registrant']

        assert len(registrants) == 1
        registrant = registrants[0]

        registrant_id = registrant.pop('id')
        if registrant['entity_type'] == 'person':
            registrant['person_id'] = self.person_importer.resolve_json_id(
                registrant_id)
        elif registrant['entity_type'] == 'organization':
            registrant['organization_id'] = self.org_importer.resolve_json_id(
                registrant_id)

        # add prepared registrant
        new_related_entities.append(registrant)

        # prepare authority
        authorities = [re for re in data['related_entities']
                       if re['note'] == 'authority']

        assert len(authorities) == 1
        authority = authorities[0]

        authority_id = authority.pop('id')
        authority['organization_id'] = self.org_importer.resolve_json_id(
            authority_id)

        # add prepared authority
        new_related_entities.append(authority)

        # prepare and add disclosed_events
        disclosed_events = [re for re in data['related_entities']
                            if re['note'] == 'disclosed_event']

        for event in disclosed_events:
            event_id = event.pop('id')
            event['event_id'] = self.event_importer.resolve_json_id(
                event_id)
            new_related_entities.append(event)

        data['related_entities'] = new_related_entities
        data['jurisdiction_id'] = self.jurisdiction_id

        return data
