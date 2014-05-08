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
                      'related_bills': {},
                      'sponsors': {},
                      'sources': {},
                      'documents': {'links': {}},
                      'versions': {'links': {}},
                     }

    def __init__(self, jurisdiction_id, org_importer):
        super(BillImporter, self).__init__(jurisdiction_id)
        self.org_importer = org_importer

    def get_object(self, bill):
        spec = {
            'session__name': bill['session'],
            'session__jurisdiction_id': self.jurisdiction_id,
            'name': bill['name'],
        }

        # TODO: handle from_organization

        return self.model_class.objects.get(**spec)

    def prepare_for_db(self, data):
        data['name'] = fix_bill_id(data['name'])
        data['session'] = JurisdictionSession.objects.get(jurisdiction_id=self.jurisdiction_id,
                                                          name=data['session'])
        # TODO: stop this
        data.pop('actions')
        data.pop('organization')
        data.pop('chamber')
        data.pop('subject')
        return data
