import datetime
from pupa.core import db
from .base import update_object, insert_object
from .organizations import import_organization


def import_jurisdiction(jurisdiction):
    metadata = jurisdiction.get_metadata()

    metadata['_type'] = 'metadata'
    metadata['_id'] = jurisdiction.organization_id
    metadata['latest_update'] = datetime.datetime.utcnow()

    # XXX: validate metadata

    db.metadata.save(metadata)

    orgs = {'insert': 0, 'update': 0, 'noop': 0}

    # create organization
    org = {'_type': 'organization',
           'classification': 'jursidiction',
           'parent_id': None,
           'jurisdiction_id': metadata['id'],
           'name': metadata['name']
          }
    if 'other_names' in metadata:
        org['other_names'] = metadata['other_names']
    if 'parent_id' in metadata:
        org['parent_id'] = metadata['parent_id']

    result = import_organization(org)
    orgs[result] += 1

    # create parties
    for party in metadata['parties']:
        org = {'_type': 'organization',
               'classification': 'party',
               'name': party['name'],
               'parent_id': None }
        result = import_organization(org)
        orgs[result] += 1
