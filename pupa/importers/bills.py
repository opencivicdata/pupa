from pupa.core import db
from pupa.utils import fix_bill_id
from .base import BaseImporter


class BillImporter(BaseImporter):
    _type = 'bill'

    def get_db_spec(self, bill):
        spec = {'jurisdiction_id': bill['jurisdiction_id'],
                'session': bill['session'],
                'name': bill['name'],
               }
        if 'chamber' in bill:
            spec['chamber'] = bill['chamber']
        return spec

    def prepare_object_from_json(self, obj):
        obj['name'] = fix_bill_id(obj['name'])
        if 'alternate_bill_ids' in obj:
            obj['alternate_bill_ids'] = [fix_bill_id(bid) for bid in
                                         obj['alternate_bill_ids']]

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
