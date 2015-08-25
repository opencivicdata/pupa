from opencivicdata.models import VoteEvent, VoteCount, PersonVote, VoteSource
from .base import BaseImporter
from ..exceptions import InvalidVoteEventError


class VoteEventImporter(BaseImporter):
    _type = 'vote_event'
    model_class = VoteEvent
    related_models = {'counts': (VoteCount, 'vote_id', {}),
                      'votes': (PersonVote, 'vote_id', {}),
                      'sources': (VoteSource, 'vote_event_id', {})}

    def __init__(self, jurisdiction_id, person_importer, org_importer,
                 bill_importer):

        super(VoteEventImporter, self).__init__(jurisdiction_id)
        self.person_importer = person_importer
        self.bill_importer = bill_importer
        self.org_importer = org_importer
        self.seen_bill_ids = set()
        self.vote_events_to_delete = set()

    def get_object(self, vote_event):
        spec = {'legislative_session_id': vote_event['legislative_session_id']}

        if not vote_event['identifier'] and not vote_event['bill_id']:
            raise InvalidVoteEventError(
                'attempt to save a VoteEvent without an "identifier" or "bill_id"')

        if vote_event['bill_id']:
            if vote_event['bill_id'] not in self.seen_bill_ids:
                self.seen_bill_ids.add(vote_event['bill_id'])
                # keep a list of all the vote event ids that should be deleted
                self.vote_events_to_delete.update(
                    self.model_class.objects.filter(bill_id=vote_event['bill_id']).values_list(
                        'id', flat=True)
                )
            spec['bill_id'] = vote_event['bill_id']

        if vote_event['identifier']:
            # if there's an identifier, just use it and the bill_id and the session
            spec['identifier'] = vote_event['identifier']
        else:
            # otherwise use the motion, start_date, and org as well
            spec.update({
                'motion_text': vote_event['motion_text'],
                'start_date': vote_event['start_date'],
                'organization_id': vote_event['organization_id']
            })

        return self.model_class.objects.get(**spec)

    def prepare_for_db(self, data):
        data['legislative_session_id'] = self.get_session_id(data.pop('legislative_session'))
        data['organization_id'] = self.org_importer.resolve_json_id(data.pop('organization'))
        data['bill_id'] = self.bill_importer.resolve_json_id(data.pop('bill'))
        return data

    def postimport(self):
        # be sure not to delete vote events that were imported (meaning updated) this time through
        self.vote_events_to_delete.difference_update(self.json_to_db_id.values())
        # everything remaining, goodbye
        self.model_class.objects.filter(id__in=self.vote_events_to_delete).delete()
