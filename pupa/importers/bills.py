from pupa.utils import fix_bill_id
from opencivicdata.models import (Bill, BillSummary, BillTitle, BillName, RelatedBill,
                                  BillSponsor, BillDocument, BillVersion, BillDocumentLink,
                                  BillVersionLink, BillSource, JurisdictionSession)
from .base import BaseImporter


class BillImporter(BaseImporter):
    _type = 'bill'
    model_class = Bill
    related_models = {'summaries': {},
                      'other_titles': {},
                      'other_names': {},
                      'actions': {'related_entities': {}},
                      'related_bills': {},
                      'sponsors': {},
                      'sources': {},
                      'documents': {'links': {}},
                      'versions': {'links': {}},
                     }
    preserve_order = {'actions'}

    def __init__(self, jurisdiction_id, org_importer):
        super(BillImporter, self).__init__(jurisdiction_id)
        self.org_importer = org_importer

    def get_object(self, bill):
        spec = {
            'session__name': bill['session'],
            'session__jurisdiction_id': self.jurisdiction_id,
            'name': bill['name'],
        }

        # TODO: use  from_org

        return self.model_class.objects.get(**spec)

    def prepare_for_db(self, data):
        data['name'] = fix_bill_id(data['name'])
        data['session'] = JurisdictionSession.objects.get(jurisdiction_id=self.jurisdiction_id,
                                                          name=data['session'])

        if data['from_organization']:
            data['from_organization_id'] = self.org_importer.resolve_json_id(
                data.pop('from_organization'))

        return data

    def prepare_subobj_for_db(self, field_name, data):
        if field_name == 'related_bills':
            newdata = {'relation_type': data['relation_type']}
            newdata['related_bill'] = self.get_object(data)
            return newdata

        return data
