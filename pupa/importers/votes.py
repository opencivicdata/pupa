from .base import BaseImporter
from opencivicdata.models import VoteEvent, LegislativeSession


class VoteImporter(BaseImporter):
    _type = 'vote'
    model_class = VoteEvent
    related_models = {'counts': {}, 'votes': {}, 'sources': {}}

    def __init__(self, jurisdiction_id,
                 person_importer, org_importer, bill_importer):

        super(VoteImporter, self).__init__(jurisdiction_id)
        self.person_importer = person_importer
        self.bill_importer = bill_importer
        self.org_importer = org_importer
        self.seen_bill_ids = set()

    def get_object(self, vote):
        if vote['identifier']:
            spec = {
                'legislative_session': vote['legislative_session'],
                'identifier': vote['identifier'],
            }
        elif vote['bill_id']:
            if vote['bill_id'] not in self.seen_bill_ids:
                self.seen_bill_ids.add(vote['bill_id'])
                self.model_class.objects.filter(bill_id=vote['bill_id']).delete()
            spec = {
                'legislative_session': vote['legislative_session'],
                'bill_id': vote['bill_id'],
                'motion_text': vote['motion_text'],
                'start_date': vote['start_date'],
            }
        else:
            raise ValueError('attempt to save a Vote without an "identifier" or "bill_id"')
        return self.model_class.objects.get(**spec)

    def prepare_for_db(self, data):
        data['legislative_session'] = LegislativeSession.objects.get(
            identifier=data.pop('legislative_session'), jurisdiction_id=self.jurisdiction_id)
        data['organization_id'] = self.org_importer.resolve_json_id(data.pop('organization'))
        data['bill_id'] = self.bill_importer.resolve_json_id(data.pop('bill'))
        return data
