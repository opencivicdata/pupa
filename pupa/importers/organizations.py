from .base import BaseImporter


class OrganizationImporter(BaseImporter):
    _type = 'organization'

    def get_db_spec(self, org):
        spec = {'classification': org['classification'],
                'name': org['name'],
                'parent_id': org.get('parent_id')}
        return spec
