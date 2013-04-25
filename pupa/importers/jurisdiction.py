import datetime
from pupa.utils import make_id
from pupa.core import db


def import_jurisdiction(jurisdiction):
    metadata = jurisdiction.get_metadata()

    metadata['_type'] = 'metadata'
    metadata['_id'] = jurisdiction.organization_id
    metadata['latest_update'] = datetime.datetime.utcnow()

    # XXX: validate metadata

    db.metadata.save(metadata)

    # create organization
    org = {'_type': 'organization',
           'classification': 'jursidiction',
           'id': metadata['_id'],
           'name': metadata['name'],
          }
    if 'other_names' in metadata:
        org['other_names'] = metadata['other_names']
    if 'parent_id' in metadata:
        org['parent_id'] = metadata['parent_id']
    db.organizations.save(org)

    # create parties
    for party in metadata['parties']:
        if not db.organizations.find({'classification': 'party',
                                      'name': party['name']}).count():
            org = {'_type': 'organization',
                   'classification': 'party',
                   'name': party['name'],
                   'id': make_id('organization')}
            db.organizations.save(org)
