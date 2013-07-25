from .base import BaseImporter


class MembershipImporter(BaseImporter):
    _type = 'membership'

    def __init__(self, jurisdiction_id, person_importer, org_importer):
        super(MembershipImporter, self).__init__(jurisdiction_id)
        self.person_importer = person_importer
        self.org_importer = org_importer

    def get_db_spec(self, membership):
        spec = {'organization_id': membership['organization_id'],
                'person_id': membership['person_id'],
                'role': membership['role'],
                # if this is a historical role, only update historical roles
                'end_date': membership.get('end_date')
               }

        if 'unmatched_legislator' in membership:
            spec['unmatched_legislator'] = membership['unmatched_legislator']

        return spec

    def prepare_object_from_json(self, obj):
        org_json_id = obj['organization_id']
        obj['organization_id'] = self.org_importer.resolve_json_id(org_json_id)
        person_json_id = obj['person_id']
        obj['person_id'] = self.person_importer.resolve_json_id(person_json_id)
        return obj
