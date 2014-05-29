from pupa.utils import fix_bill_id
from opencivicdata.models import Bill, JurisdictionSession, RelatedBill
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
                      'versions': {'links': {}}}
    preserve_order = {'actions'}

    def __init__(self, jurisdiction_id, org_importer):
        super(BillImporter, self).__init__(jurisdiction_id)
        self.org_importer = org_importer

    def get_object(self, bill):
        spec = {
            'session': bill['session'],
            'name': bill['name'],
        }
        if 'from_organization_id' in bill:
            spec['from_organization_id'] = bill['from_organization_id']

        return self.model_class.objects.get(**spec)

    def limit_spec(self, spec):
        spec['session__jurisdiction_id'] = self.jurisdiction_id
        return spec

    def prepare_for_db(self, data):
        data['name'] = fix_bill_id(data['name'])
        data['session'] = JurisdictionSession.objects.get(jurisdiction_id=self.jurisdiction_id,
                                                          name=data['session'])

        if data['from_organization']:
            data['from_organization_id'] = self.org_importer.resolve_json_id(
                data.pop('from_organization'))

        return data

    def postimport(self):
        # go through all RelatedBill objs that are attached to a bill in this jurisdiction and
        # are currently unresolved
        for rb in RelatedBill.objects.filter(bill__session__jurisdiction_id=self.jurisdiction_id,
                                             related_bill=None):
            candidates = list(Bill.objects.filter(session__name=rb.session,
                                                  session__jurisdiction_id=self.jurisdiction_id,
                                                  name=rb.name))
            if len(candidates) == 1:
                rb.related_bill = candidates[0]
                rb.save()
            elif len(candidates) > 1:
                # if we ever see this, we need to add additional fields on the relation
                raise RuntimeError('multiple related_bill candidates found for {}'.format(rb))
