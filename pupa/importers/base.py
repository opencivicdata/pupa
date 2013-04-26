import os
import glob
import json
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
    elif type_ == 'membership':
        return db.memberships
    else:
        raise ValueError('unknown type: ' + type_)


def insert_object(obj):
    """ insert a new object into the appropriate collection

    params:
        obj - object to insert

    return:
        database id of new object
    """
    # XXX: check if object already has an id?

    # add updated_at/created_at timestamp
    obj['updated_at'] = obj['created_at'] = datetime.datetime.utcnow()
    obj['_id'] = make_id(obj['_type'])
    collection = collection_for_type(obj['_type'])

    collection.save(obj)
    return obj['_id']


def update_object(old, new):
    """
        update an existing object with a new one, only saving it and
        setting updated_at if something changed

        params:
            old: old object
            new: new object

        returns:
            database_id     id of object in db
            was_updated     whether or not the object was updated
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

    return old['_id'], updated


class BaseImporter(object):

    def __init__(self, jurisdiction_id):
        self.jurisdiction_id = jurisdiction_id
        self.collection = collection_for_type(self._type)
        self.results = {'insert': 0, 'update': 0, 'noop': 0}
        self.json_to_db_id = {}

    def import_object(self, obj):
        spec = self.get_db_spec(obj)

        db_obj = self.collection.find_one(spec)

        if db_obj:
            _id, updated = update_object(db_obj, obj)
            self.results['update' if updated else 'noop'] += 1
        else:
            _id = insert_object(obj)
            self.results['insert'] += 1

        return _id

    def import_from_json(self, datadir):
        # load all json, mapped by json_id
        raw_objects = {}
        for fname in glob.glob(os.path.join(datadir, self._type + '_*.json')):
            with open(fname) as f:
                data = json.load(f)
                # prepare object from json
                data['jurisdiction_id'] = self.jurisdiction_id
                json_id = data.pop('_id')
                data = self.prepare_object_from_json(data)
                raw_objects[json_id] = data

        # map duplicate ids to first occurance of same object
        duplicates = {}
        for json_id, obj in raw_objects.items():
            for json_id2, obj2 in raw_objects.items():
                if json_id != json_id2 and obj == obj2:
                    duplicates[json_id2] = json_id

        # now do import, ignoring duplicates
        for json_id, obj in raw_objects.items():
            if json_id not in duplicates:
                self.json_to_db_id[json_id] = self.import_object(obj)

        print self._type, self.results

    def resolve_json_id(self, json_id):
        """
            Given an id found in scraped JSON, return a DB id for the object.

            params:
                json_id:    id from json

            returns:
                database id

            raises:
                ValueError if id couldn't be resolved
        """
        # make sure this sort of looks like a UUID
        if len(json_id) != 36:
            raise ValueError('cannot resolve non-uuid: {0}'.format(json_id))

        try:
            return self.json_to_db_id[json_id]
        except KeyError:
            raise ValueError('cannot resolve id: {0}'.format(json_id))

    def prepare_object_from_json(self, obj):
        # no-op by default
        return obj
