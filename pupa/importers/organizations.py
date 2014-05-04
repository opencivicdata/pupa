from opencivicdata.models import (Organization, OrganizationIdentifier, OrganizationName,
                                  OrganizationContactDetail, OrganizationLink, OrganizationSource)
from .base import BaseImporter


class OrganizationImporter(BaseImporter):
    _type = 'organization'
    model_class = Organization
    related_models = {'identifiers': OrganizationIdentifier,
                      'other_names': OrganizationName,
                      'contact_details': OrganizationContactDetail,
                      'links': OrganizationLink,
                      'sources': OrganizationSource}

    def get_object(self, org):
        spec = {'classification': org['classification'],
                'name': org['name'],
                'parent_id': org['parent_id']}

        # add jurisdiction_id unless this is a party
        if org['classification'] != 'party':
            spec['jurisdiction_id'] = org.get('jurisdiction_id')

        return self.model_class.objects.get(**spec)

    def prepare_for_db(self, data):
        data['jurisdiction_id'] = self.jurisdiction_id
        return data

    def resolve_json_id(self, json_id):
        # handle special party:* and jurisdiction:* ids first
        if json_id.startswith('party:'):
            id_piece = json_id[6:]
            return Organization.objects.get(classification='party', name=id_piece).id
        elif json_id.startswith('jurisdiction:'):
            _, chamber, id_piece = json_id.split(':', 2)
            print(chamber, id_piece)
            return Organization.objects.get(classification='legislature', chamber=chamber,
                                            jurisdiction_id=id_piece).id

        # or just resolve the normal way
        return super(OrganizationImporter, self).resolve_json_id(json_id)
