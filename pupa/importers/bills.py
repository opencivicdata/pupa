from pupa.core import db
from pupa.utils import fix_bill_id
from pupa.models import Bill
from .base import BaseImporter


class BillImporter(BaseImporter):
    _type = 'bill'
    _model_class = Bill

    def __init__(self, jurisdiction_id, org_importer):
        super(BillImporter, self).__init__(jurisdiction_id)
        self.org_importer = org_importer

    def get_db_spec(self, bill):
        spec = {'jurisdiction_id': bill.jurisdiction_id,
                'session': bill.session,
                'name': bill.name}

        if hasattr(bill, 'chamber') and bill.chamber is not None:
            spec['chamber'] = bill.chamber

        return spec

    def prepare_object_from_json(self, obj):
        obj['name'] = fix_bill_id(obj['name'])
        org = self.org_importer._resolve_org_by_chamber(self.jurisdiction_id, obj['organization'])

        obj['organization'] = org['_id']

        if 'alternate_bill_ids' in obj:
            obj['alternate_bill_ids'] = [fix_bill_id(bid) for bid in obj['alternate_bill_ids']]

        # XXX: subject categorizer
        # XXX: action categorizer

        for rel in obj['related_bills']:
            rel['bill_id'] = fix_bill_id(rel['bill_id'])
            spec = rel.copy()
            spec['jurisdiction_id'] = obj['jurisdiction_id']
            rel_obj = db.bills.find_one(spec)
            if rel_obj:
                rel['internal_id'] = rel_obj['_id']
            else:
                self.logger.warning('Unknown related bill: {chamber} '
                                    '{session} {bill_id}'.format(**rel))

        return obj
