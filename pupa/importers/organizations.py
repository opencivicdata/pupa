import json
from opencivicdata.models import (Organization, OrganizationIdentifier, OrganizationName,
                                  OrganizationContactDetail, OrganizationLink, OrganizationSource)
from .base import BaseImporter


class OrganizationImporter(BaseImporter):
    _type = 'organization'
    model_class = Organization
    related_models = {'identifiers': {},
                      'other_names': {},
                      'contact_details': {},
                      'links': {},
                      'sources': {}
                     }

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
        if data['classification'] != 'party':
            data['jurisdiction_id'] = self.jurisdiction_id
        return data

    def resolve_json_id(self, json_id):
        # handle special psuedo-ids
        if json_id.startswith('~'):
            spec = json.loads(json_id[1:])
            if spec.get('classification') != 'party':
                spec['jurisdiction_id'] = self.jurisdiction_id
            return Organization.objects.get(**spec).id

        # or just resolve the normal way
        return super(OrganizationImporter, self).resolve_json_id(json_id)
