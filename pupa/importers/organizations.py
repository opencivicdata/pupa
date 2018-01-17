from django.db.models import Q
from opencivicdata.core.models import (Organization, OrganizationIdentifier, OrganizationName,
                                       OrganizationContactDetail, OrganizationLink,
                                       OrganizationSource)
from .base import BaseImporter
from ..utils import get_pseudo_id
from ..utils.topsort import Network
from ..exceptions import UnresolvedIdError, PupaInternalError, SameOrgNameError


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
                'parent_id': org['parent_id']}

        # add jurisdiction_id unless this is a party
        jid = org.get('jurisdiction_id')
        if jid:
            spec['jurisdiction_id'] = jid

        all_names = [org['name']] + [o['name'] for o in org['other_names']]

        query = (Q(**spec) &
                 (Q(name__in=all_names) | Q(other_names__name__in=all_names)))
        matches = list(self.model_class.objects.filter(query).distinct('id'))
        matches_length = len(matches)
        if matches_length == 1:
            return matches[0]
        elif matches_length == 0:
            raise self.model_class.DoesNotExist(
                'No Organization: {} in {}'.format(all_names, self.jurisdiction_id))
        else:
            raise SameOrgNameError(org['name'])

    def prepare_for_db(self, data):
        data['parent_id'] = self.resolve_json_id(data['parent_id'])

        if data['classification'] != 'party':
            data['jurisdiction_id'] = self.jurisdiction_id
        return data

    def limit_spec(self, spec):
        if spec.get('classification') != 'party':
            spec['jurisdiction_id'] = self.jurisdiction_id

        name = spec.pop('name', None)
        if name:
            return (Q(**spec) &
                    (Q(name=name) | Q(other_names__name=name)))
        return spec

    def _prepare_imports(self, dicts):
        """ an override for prepare imports that sorts the imports by parent_id dependencies """
        # all pseudo parent ids we've seen
        pseudo_ids = set()
        # pseudo matches
        pseudo_matches = {}

        # get prepared imports from parent
        prepared = dict(super(OrganizationImporter, self)._prepare_imports(dicts))

        # collect parent pseudo_ids
        for _, data in prepared.items():
            parent_id = data.get('parent_id', None) or ''
            if parent_id.startswith('~'):
                pseudo_ids.add(parent_id)

        # turn pseudo_ids into a tuple of dictionaries
        pseudo_ids = [(ppid, get_pseudo_id(ppid)) for ppid in pseudo_ids]

        # loop over all data again, finding the pseudo ids true json id
        for json_id, data in prepared.items():
            # check if this matches one of our ppids
            for ppid, spec in pseudo_ids:
                match = True
                for k, v in spec.items():
                    if data[k] != v:
                        match = False
                        break
                if match:
                    if ppid in pseudo_matches:
                        raise UnresolvedIdError('multiple matches for pseudo id: ' + ppid)
                    pseudo_matches[ppid] = json_id

        # toposort the nodes so parents are imported first
        network = Network()
        in_network = set()
        import_order = []

        for json_id, data in prepared.items():
            parent_id = data.get('parent_id', None)

            # resolve pseudo_ids to their json id before building the network
            if parent_id in pseudo_matches:
                parent_id = pseudo_matches[parent_id]

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
            raise PupaInternalError("import is missing nodes in network set")

        return import_order
