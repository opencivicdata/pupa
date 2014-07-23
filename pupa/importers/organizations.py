from opencivicdata.models import (Organization, OrganizationIdentifier, OrganizationName,
                                  OrganizationContactDetail, OrganizationLink, OrganizationSource)
from .base import BaseImporter
from ..utils import get_psuedo_id
from ..utils.topsort import Network


class OrganizationImporter(BaseImporter):
    _type = 'organization'
    model_class = Organization
    related_models = {'identifiers': (OrganizationIdentifier, 'organization_id', {}),
                      'other_names': (OrganizationName, 'organization_id', {}),
                      'contact_details': (OrganizationContactDetail, 'organization_id', {}),
                      'links': (OrganizationLink, 'organization_id', {}),
                      'sources': (OrganizationSource, 'organization_id', {}),
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
        data['parent_id'] = self.resolve_json_id(data['parent_id'])

        if data['classification'] != 'party':
            data['jurisdiction_id'] = self.jurisdiction_id
        return data

    def limit_spec(self, spec):
        if spec.get('classification') != 'party':
            spec['jurisdiction_id'] = self.jurisdiction_id
        return spec

    def _prepare_imports(self, dicts):
        """ an override for prepare imports that sorts the imports by parent_id dependencies """
        # all psuedo parent ids we've seen
        psuedo_ids = set()
        # psuedo matches
        psuedo_matches = {}
        # all data items with a psuedo_id parent
        psuedo_children = []

        # get prepared imports from parent
        prepared = dict(super(OrganizationImporter, self)._prepare_imports(dicts))

        # collect parent psuedo_ids
        for _, data in prepared.items():
            parent_id = data.get('parent_id', None) or ''
            if parent_id.startswith('~'):
                psuedo_ids.add(parent_id)

        # turn psuedo_ids into a tuple of dictionaries
        psuedo_ids = [(ppid, get_psuedo_id(ppid)) for ppid in psuedo_ids]

        # loop over all data again, finding the psuedo ids true json id
        for json_id, data in prepared.items():
            # check if this matches one of our ppids
            for ppid, spec in psuedo_ids:
                match = True
                for k, v in spec.items():
                    if data[k] != v:
                        match = False
                        break
                if match:
                    if ppid in psuedo_matches:
                        raise Exception("multiple matches for psuedo-id " + ppid)
                    psuedo_matches[ppid] = json_id

        # toposort the nodes so parents are imported first
        network = Network()
        in_network = set()
        import_order = []

        for json_id, data in prepared.items():
            parent_id = data.get('parent_id', None)

            # resolve psuedo_ids to their json id before building the network
            if parent_id in psuedo_matches:
                parent_id = psuedo_matches[parent_id]

            network.add_node(json_id)
            if parent_id:
                # Right. There's an import dep. We need to add the edge from
                # the parent to the current node, so that we import the parent
                # before the current node.
                network.add_edge(parent_id, json_id)

        # resolve the sorted import order
        for jid in network.sort():
            import_order.append((jid, prepared[jid]))
            in_network.add(jid)

        # ensure all data made it into network (paranoid check, should never fail)
        if in_network != set(prepared.keys()):    # pragma: no cover
            raise Exception("import is missing nodes in network set")

        return import_order
