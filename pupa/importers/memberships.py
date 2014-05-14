from opencivicdata.models import Membership
from .base import BaseImporter


class MembershipImporter(BaseImporter):
    _type = 'membership'
    model_class = Membership
    related_models = {'contact_details': {}, 'links': {}}

    def __init__(self, jurisdiction_id, person_importer, org_importer, post_importer):
        super(MembershipImporter, self).__init__(jurisdiction_id)
        self.person_importer = person_importer
        self.org_importer = org_importer
        self.post_importer = post_importer

    def get_object(self, membership):
        spec = {'organization_id': membership['organization_id'],
                'person_id': membership['person_id'],
                'label': membership['label'],
                # if this is a historical role, only update historical roles
                'end_date': membership['end_date']}

        # post_id is optional - might exist in DB but not scraped here?
        if membership['post_id']:
            spec['post_id'] = membership['post_id']

        return self.model_class.objects.get(**spec)

    def prepare_for_db(self, data):
        data['organization_id'] = self.org_importer.resolve_json_id(data['organization_id'])
        data['person_id'] = self.person_importer.resolve_json_id(data['person_id'])
        data['post_id'] = self.post_importer.resolve_json_id(data['post_id'])
        return data
