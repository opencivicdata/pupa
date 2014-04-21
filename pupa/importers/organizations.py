from pupa.models import (Organization, OrganizationIdentifier, OrganizationName,
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

    def _resolve_org_by_chamber(self, jurisdiction_id, chamber):
        """
        This is used by the other importers to match an org based on ``chamber`` if it exists.
        """
        org = Organization.objects.get(classification='legislature',
                                       jurisdiction_id=jurisdiction_id,
                                       chamber=chamber)

    def resolve_json_id(self, json_id):
        # handle special party:* and jurisdiction:* ids first
        for type_, key in (('party', 'name'), ('jurisdiction', 'jurisdiction_id')):
            if json_id.startswith(type_ + ':'):
                id_piece = json_id.split(':', 1)[1]
                try:
                    return Organization.objects.get(**{'classification': type_, key: id_piece}).id
                except Organization.DoesNotExist:
                    raise ValueError('attempt to create membership to unknown id: ' + json_id)

        # or just resolve the normal way
        return super(OrganizationImporter, self).resolve_json_id(json_id)
