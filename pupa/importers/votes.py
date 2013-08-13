from .utils import (people_by_jurisdiction_and_name,
                    orgs_by_jurisdiction_and_name,
                    bills_by_jurisdiction_and_name)

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
            bills = bills_by_jurisdiction_and_name(
                obj['jurisdiction_id'],
                bill['name'],
            )
            if bills.count() != 1:
                self.warning("Can't resolve bill `%s'" % (bill['name']))
            else:
                bill_obj = bills[0]
                bill['id'] = bill_obj['_id']

        for vote in obj['roll_call']:
            who = vote['person']
            people = people_by_jurisdiction_and_name(
                obj['jurisdiction_id'],
                who['name'],
                chamber=who.get('chamber')
            )

            if people.count() != 1:
                self.warning("can't match `%s'" % (who['name']))
                continue  # can't match

            person_obj = people[0]
            vote['id'] = person_obj['_id']

        org = obj.get('organization')
        org_id = obj.get('organization_id')

        if org and not org_id:  # OK. We have an org that needs matching.
            orgs = orgs_by_jurisdiction_and_name(
                obj['jurisdiction_id'],
                org,
            )  # get all matching orgs.

            if orgs.count() == 1:
                org_obj = orgs[0]  # Let's get the only result.
                obj['organization_id'] = org_obj['_id']
            else:
                self.warning("can't match `%s'" % (org))

        elif org_id:  # We have a sort of org ID
            if org is None:  # If we have the ID but no the name (odd...)
                raise ValueError("Someone set an org_id without an org name.")

            org_json_id = obj['organization_id']  # scrape-time match?
            if org_json_id and not org_json_id.startswith("ocd-organization"):
                obj['organization_id'] = self.org_importer.resolve_json_id(
                    org_json_id)  # resolve it.
        return obj
