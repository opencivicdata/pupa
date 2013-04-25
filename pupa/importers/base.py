import uuid
import datetime
from pupa.core import db


def make_id(type_):
    return 'ocd-{0}/{1}'.format(type_, uuid.uuid1())


def collection_for_type(type_):
    if type_ == 'metadata':
        return db.metadata
    elif type_ == 'person':
        return db.people
    elif type_ == 'organization':
        return db.organizations
    else:
        raise ValueError('unknown type: ' + type_)


def insert_object(obj):
    """ insert a new object into the appropriate collection """
    # XXX: check if object already has an id?

    # add updated_at/created_at timestamp
    obj['updated_at'] = obj['created_at'] = datetime.datetime.utcnow()
    obj['_id'] = make_id(obj['_type'])
    collection = collection_for_type(obj['_type'])

    collection.save(obj)


def update_object(old, new):
    """
        update an existing object with a new one, only saving it and
        setting updated_at if something changed

        old: old object
        new: new object
    """
    updated = False

    if old['_type'] != new['_type']:
        raise ValueError('old and new must be of same _type')
    collection = collection_for_type(new['_type'])

    # allow objects to prevent certain fields from being updated
    locked_fields = old.get('_locked_fields', [])

    for key, value in new.items():
        if key in locked_fields:
            continue

        if old.get(key) != value:
            old[key] = value
            updated = True

    if updated:
        old['updated_at'] = datetime.datetime.utcnow()
        collection.save(old)

    return updated
