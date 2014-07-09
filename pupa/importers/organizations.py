from opencivicdata.models import Organization
from .base import BaseImporter


class OrganizationImporter(BaseImporter):
    _type = 'organization'
    model_class = Organization
    related_models = {'identifiers': {}, 'other_names': {}, 'contact_details': {}, 'links': {},
                      'sources': {}}

    def get_object(self, org):
        spec = {'classification': org['classification'],
                'name': org['name'],
                'parent_id': org['parent_id']}

        # add jurisdiction_id unless this is a party
        jid = org.get('jurisdiction_id')
        if jid:
            spec['jurisdiction_id'] = jid

        return self.model_class.objects.get(**spec)

    def prepare_for_db(self, data):
        data['parent_id'] = self.resolve_json_id(data['parent_id'])

        if data['classification'] != 'party':
            data['jurisdiction_id'] = self.jurisdiction_id
        return data

    def limit_spec(self, spec):
        if spec.get('classification') != 'party':
            spec['jurisdiction_id'] = self.jurisdiction_id
        return spec
