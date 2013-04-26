from .base import BaseImporter
from pupa.core import db


class OrganizationImporter(BaseImporter):
    _type = 'organization'

    def get_db_spec(self, org):
        spec = {'classification': org['classification'],
                'name': org['name'],
                'parent_id': org.get('parent_id')}
        return spec

    def resolve_json_id(self, json_id):
        # handle special party:* and jurisdiction:* ids first
        for type_, key in (('party', 'name'),
                           ('jurisdiction', 'jurisdiction_id')):
            if json_id.startswith(type_ + ':'):
                id_piece = json_id.split(':', 1)[1]
                org = db.organizations.find_one(
                    {'classification': type_, key: id_piece})
                if not org:
                    raise ValueError('attempt to create membership to unknown '
                                     + type_ + ': ' + id_piece)
                else:
                    return org['_id']

        # just resolve the normal way
        return super(OrganizationImporter, self).resolve_json_id(json_id)
