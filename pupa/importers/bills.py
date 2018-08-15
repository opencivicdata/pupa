from opencivicdata.legislative.models import (Bill, RelatedBill, BillAbstract, BillTitle,
                                              BillIdentifier, BillAction, BillActionRelatedEntity,
                                              BillSponsorship, BillSource, BillDocument,
                                              BillVersion, BillDocumentLink, BillVersionLink)
from .base import BaseImporter
from ..exceptions import PupaInternalError


class BillImporter(BaseImporter):
    _type = 'bill'
    model_class = Bill
    related_models = {'abstracts': (BillAbstract, 'bill_id', {}),
                      'other_titles': (BillTitle, 'bill_id', {}),
                      'other_identifiers': (BillIdentifier, 'bill_id', {}),
                      'actions': (BillAction, 'bill_id', {
                          'related_entities': (BillActionRelatedEntity, 'action_id', {})}),
                      'related_bills': (RelatedBill, 'bill_id', {}),
                      'sponsorships': (BillSponsorship, 'bill_id', {}),
                      'sources': (BillSource, 'bill_id', {}),
                      'documents': (BillDocument, 'bill_id', {
                          'links': (BillDocumentLink, 'document_id', {})}),
                      'versions': (BillVersion, 'bill_id', {
                          'links': (BillVersionLink, 'version_id', {})}),
                      }
    preserve_order = {'actions'}

    def __init__(self, jurisdiction_id, org_importer, person_importer):
        super(BillImporter, self).__init__(jurisdiction_id)
        self.org_importer = org_importer
        self.person_importer = person_importer

    def get_object(self, bill):
        spec = {
            'legislative_session_id': bill['legislative_session_id'],
            'identifier': bill['identifier'],
        }
        if 'from_organization_id' in bill:
            spec['from_organization_id'] = bill['from_organization_id']

        return self.model_class.objects.prefetch_related('actions__related_entities',
                                                         'versions__links',
                                                         'documents__links',
                                                         ).get(**spec)

    def limit_spec(self, spec):
        spec['legislative_session__jurisdiction_id'] = self.jurisdiction_id
        return spec

    def prepare_for_db(self, data):
        data['legislative_session_id'] = self.get_session_id(data.pop('legislative_session'))

        if data['from_organization']:
            data['from_organization_id'] = self.org_importer.resolve_json_id(
                data.pop('from_organization'))

        for action in data['actions']:
            action['organization_id'] = self.org_importer.resolve_json_id(
                action['organization_id'])
            for entity in action['related_entities']:
                if 'organization_id' in entity:
                    entity['organization_id'] = self.org_importer.resolve_json_id(
                        entity['organization_id'])
                elif 'person_id' in entity:
                    entity['person_id'] = self.person_importer.resolve_json_id(
                        entity['person_id'])

        for sponsor in data['sponsorships']:
            if 'person_id' in sponsor:
                sponsor['person_id'] = self.person_importer.resolve_json_id(
                    sponsor['person_id'], allow_no_match=True)

            if 'organization_id' in sponsor:
                sponsor['organization_id'] = self.org_importer.resolve_json_id(
                    sponsor['organization_id'], allow_no_match=True)

        return data

    def postimport(self):
        # go through all RelatedBill objs that are attached to a bill in this jurisdiction and
        # are currently unresolved
        for rb in RelatedBill.objects.filter(
                bill__legislative_session__jurisdiction_id=self.jurisdiction_id,
                related_bill=None):
            candidates = list(Bill.objects.filter(
                legislative_session__identifier=rb.legislative_session,
                legislative_session__jurisdiction_id=self.jurisdiction_id,
                identifier=rb.identifier)
            )
            if len(candidates) == 1:
                rb.related_bill = candidates[0]
                rb.save()
            elif len(candidates) > 1:    # pragma: no cover
                # if we ever see this, we need to add additional fields on the relation
                raise PupaInternalError('multiple related_bill candidates found for {}'.format(rb))
