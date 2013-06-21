from .base import BaseImporter
import pupa.core


class VoteImporter(BaseImporter):
    _type = 'vote'

    def get_db_spec(self, event):
        spec = {
            "motion": event['motion'],
            "chamber": event['chamber'],
            "date": event['date'],
        }
        return spec

    def prepare_object_from_json(self, obj):
        bill = obj.get('bill', None)
        if bill:
            bill_obj = pupa.core.db.bills.find_one({"name": bill['name']})
            # XXX: use all_names above
            if bill_obj is None:
                self.warning("Can't resolve bill `%s'" % (bill['name']))
            else:
                bill['id'] = bill_obj['_id']

        for vote in obj['roll_call']:
            who = vote['person']
            person_obj = pupa.core.db.people.find_one({
                "name": who['name'],
                "chamber": who.get('chamber', None),
            })
            if person_obj is None:
                self.warning("Can't resolve person `%s'" % (who['name']))
            else:
                vote['person']['id'] = person_obj['_id']

        return obj
