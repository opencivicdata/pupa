from .base import BaseImporter
from opencivicdata.models import (Disclosure,
                                  DisclosureSource,
                                  DisclosureRegistrant,
                                  DisclosureAuthority,
                                  DisclosureDocument, DisclosureDocumentLink,
                                  DisclosureRelatedEntity,
                                  DisclosureDisclosedEvent,
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
        'disclosed_events': (DisclosureDisclosedEvent, 'disclosure_id', {}),
        #'registrant': (DisclosureRegistrant, 'disclosure_id', {}),
        #'authority': (DisclosureAuthority, 'disclosure_id', {}),
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
        del data['registrant_id']
        del data['authority_id']
        
        registrants = [re for re in data['related_entities']
                      if re['note'] == 'registrant']

        assert len(registrants) == 1
        registrant = registrants[0]
        
        authorities = [re for re in data['related_entities']
                       if re['note'] == 'authority']

        assert len(authorities) == 1
        authority = authorities[0]
        
        # if registrant['entity_type'] == 'person':
        #     registrant['id'] = self.person_importer.resolve_json_id(
        #         registrant['id'])
        # elif registrant['entity_type'] == 'organization':
        #     registrant['id'] = self.org_importer.resolve_json_id(
        #         registrant['id'])

        del data['registrant']
        del data['authority']

        data['related_entities'] = [registrant,]

        #data['registrant'] = registrant
        #data['authority'] = authority


        for event in data['disclosed_events']:
            event_id = event.pop('id')
            event['event_id'] = self.event_importer.resolve_json_id(
                event_id)


        data['jurisdiction_id'] = self.jurisdiction_id

        return data
