from opencivicdata.core.models import Membership, MembershipContactDetail, MembershipLink
from .base import BaseImporter
from ..utils import get_pseudo_id
from ..exceptions import NoMembershipsError


class MembershipImporter(BaseImporter):
    _type = 'membership'
    model_class = Membership
    related_models = {'contact_details': (MembershipContactDetail, 'membership_id', {}),
                      'links': (MembershipLink, 'membership_id', {})
                      }

    def __init__(self, jurisdiction_id, person_importer, org_importer, post_importer):
        super(MembershipImporter, self).__init__(jurisdiction_id)
        self.person_importer = person_importer
        self.org_importer = org_importer
        self.post_importer = post_importer
        self.seen_person_ids = set()

    def get_object(self, membership):
        spec = {'organization_id': membership['organization_id'],
                'person_id': membership['person_id'],
                'label': membership['label'],
                'role': membership['role'],
                # if this is a historical role, only update historical roles
                'end_date': membership['end_date']}

        # post_id is optional - might exist in DB but not scraped here?
        if membership['post_id']:
            spec['post_id'] = membership['post_id']

        if membership['person_name']:
            spec['person_name'] = membership['person_name']

        return self.model_class.objects.get(**spec)

    def prepare_for_db(self, data):
        # check if the organization is not tied to a jurisdiction
        if data['organization_id'].startswith('~'):
            pseudo_id = get_pseudo_id(data['organization_id'])
            is_party = (pseudo_id.get('classification') == 'party')
        else:
            # we have to assume it is not a party if we want to avoid doing a lookup here
            is_party = False

        data['organization_id'] = self.org_importer.resolve_json_id(data['organization_id'])
        data['person_id'] = self.person_importer.resolve_json_id(data['person_id'],
                                                                 allow_no_match=True)
        data['post_id'] = self.post_importer.resolve_json_id(data['post_id'])
        if not is_party:
            # track that we had a membership for this person
            self.seen_person_ids.add(data['person_id'])
        return data

    def postimport(self):
        person_ids = set(self.person_importer.json_to_db_id.values()) - self.seen_person_ids
        if person_ids:
            reverse_id_dict = {v: k for k, v in self.person_importer.json_to_db_id.items()}
            person_ids = [reverse_id_dict[pid] for pid in person_ids]
            raise NoMembershipsError(person_ids)
