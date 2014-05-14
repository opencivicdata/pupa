from .base import BaseImporter
from opencivicdata.models import VoteEvent, JurisdictionSession

class VoteImporter(BaseImporter):
    _type = 'vote'
    model_class = VoteEvent
    related_models = {'counts': {},
                      'votes': {},
                      'sources': {},
                     }

    def __init__(self, jurisdiction_id,
                 person_importer, org_importer, bill_importer):

        super(VoteImporter, self).__init__(jurisdiction_id)
        self.person_importer = person_importer
        self.bill_importer = bill_importer
        self.org_importer = org_importer

    def get_object(self, vote):
        spec = {
            'identifier': vote['identifier'],
            'session__name': vote['session'],
            'session__jurisdiction_id': self.jurisdiction_id,
        }
        # TODO: use bill, session, etc.
        return self.model_class.objects.get(**spec)

    def prepare_for_db(self, data):
        data['session'] = JurisdictionSession.objects.get(name=data.pop('session'),
                                                          jurisdiction_id=self.jurisdiction_id)
        data['organization_id'] = self.org_importer.resolve_json_id(data.pop('organization'))
        data['bill_id'] = self.bill_importer.resolve_json_id(data.pop('bill'))
        return data

    def prepare_object_from_json(self, obj):
        bill = obj.get('bill', None)
        if bill:
            if bill.get('id'):
                # We've been given a hard ID. Let's use it to match against
                # the real bill. (since the scraper knew what they were doing)
                bill['id'] = self.bill_importer.resolve_json_id(bill['id'])
            else:
                # OK. Right. We weren't given an ID. Let's try to do a
                # match by name.
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
            vote['person']['id'] = person_obj['_id']

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
