from .base import BaseImporter
import pupa.core


class VoteImporter(BaseImporter):
    _type = 'vote'

    def __init__(self, jurisdiction_id, person_importer, org_importer):
        super(VoteImporter, self).__init__(jurisdiction_id)
        self.person_importer = person_importer
        self.org_importer = org_importer

    def get_db_spec(self, event):
        spec = {
            "motion": event['motion'],
            "chamber": event['chamber'],
            "date": event['date'],
            "jurisdiction_id": event['jurisdiction_id'],
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
                person_json_id = person_obj['person_id']
                if person_json_id:
                    vote['id'] = self.person_importer.resolve_json_id(
                        person_json_id)

        org = obj.get('organization')
        if org:
            org_id = obj.get('organization_id')
            if org_id is None:
                # OK. Let's see if we can match this.

                orgs = pupa.core.db.organizations.find({
                    "jurisdiction_id": obj['jurisdiction_id'],
                    "name": org,
                })

                if orgs.count() != 1:
                    self.warning("Can't track down org `%s'" % (org))
                else:
                    orga = orgs[0]
                    obj['organization_id'] = orga['_id']

        org_json_id = obj['organization_id']
        if org_json_id and not org_json_id.startswith("ocd-organization"):
            obj['organization_id'] = self.org_importer.resolve_json_id(
                org_json_id)
        return obj
