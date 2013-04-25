import os
import glob
import json
import datetime
from pupa.core import db
from .base import update_object, insert_object


def import_organization(org):
    """
        takes an org dict and imports/updates it in database

        returns 'insert', 'update', 'noop'
    """
    spec = {'classification': org['classification'],
            'name': org['name'],
            'parent_id': org.get('parent_id')}
    db_org = db.organizations.find_one(spec)
    if db_org:
        updated = update_object(db_org, org)
        return 'update' if updated else 'noop'
    else:
        insert_object(org)
        return 'insert'


def import_organizations(jurisdiction, datadir):
    results = {'insert': 0, 'update': 0, 'noop': 0}

    # load all org json, mapped by json_id
    raw_organizations = {}
    for fname in glob.glob(os.path.join(datadir, 'organization_*.json')):
        with open(fname) as f:
            data = json.load(f)
            json_id = data.pop('_id')
            raw_organizations[json_id] = data

    # map duplicate ids to first occurance of same object
    duplicates = {}
    for json_id, org in raw_organizations.items():
        for json_id2, org2 in raw_organizations.items():
            if json_id != json_id2 and org == org2:
                duplicates[json_id2] = json_id

    # now do import
    for json_id, org in raw_organizations.items():
        if json_id not in duplicates:
            import_organization(org)
            result = import_organization(org)
            results[result] += 1

    print results
