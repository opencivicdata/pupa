import os
import glob
import json
import uuid
import logging
import datetime
from pupa.core import db


def make_id(type_):
    return 'ocd-{0}/{1}'.format(type_, uuid.uuid1())


def insert_object(obj):
    """ insert a new object into the appropriate collection

    params:
        obj - object to insert

    return:
        database id of new object
    """
    # XXX: check if object already has an id?

    # add updated_at/created_at timestamp
    obj.updated_at = obj.created_at = datetime.datetime.utcnow()
    obj._id = make_id(obj._type)

    obj.save()
    return obj._id


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

    if old._type != new._type:
        raise ValueError('old and new must be of same _type')

    # allow objects to prevent certain fields from being updated
    locked_fields = old._meta.get('locked_fields', [])

    for key, value in new.as_dict().items():
        if key in locked_fields or key == '_id':
            continue

        if not hasattr(old, key) or getattr(old, key) != value:
            # If we have a *new* value, let's update.
            setattr(old, key, value)
            updated = True

    if updated:
        old.updated_at = datetime.datetime.utcnow()
        old.save()

    return old._id, updated


class BaseImporter(object):

    def __init__(self, jurisdiction_id):
        self.jurisdiction_id = jurisdiction_id
        self.collection = db[self._model_class._collection]
        self.results = {'insert': 0, 'update': 0, 'noop': 0}
        self.json_to_db_id = {}
        self.logger = logging.getLogger("pupa")
        self.info = self.logger.info
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical

    def import_object(self, obj):
        if isinstance(obj, dict):
            raise ValueError("It appears that we're trying to import a dict.")

        spec = self.get_db_spec(obj)

        db_obj = self.collection.find_one(spec)

        if db_obj:
            db_obj = self._model_class.from_dict(db_obj)
            _id, updated = update_object(db_obj, obj)
            self.results['update' if updated else 'noop'] += 1
        else:
            _id = insert_object(obj)
            self.results['insert'] += 1
        return _id

    def dedupe_json_id(self, jid):
        nid = self.duplicates.get(jid, jid)
        if nid != jid:
            return self.dedupe_json_id(nid)
        return jid

    def import_from_json(self, datadir):
        # load all json, mapped by json_id
        raw_objects = {}
        for fname in glob.glob(os.path.join(datadir, self._type + '_*.json')):
            with open(fname) as f:
                data = json.load(f)
                # prepare object from json
                if data['_type'] != 'person':
                    data['jurisdiction_id'] = self.jurisdiction_id
                data = self.prepare_object_from_json(data)
                # convert dict=>class and store in raw_objects
                obj = self._model_class.from_dict(data)
                json_id = obj._id
                raw_objects[json_id] = obj

        # map duplicate ids to first occurance of same object
        duplicates = {}
        items = list(raw_objects.items())
        for i, (json_id, obj) in enumerate(items):
            for json_id2, obj2 in items[i+1:]:
                if json_id != json_id2 and obj == obj2:
                    duplicates[json_id2] = json_id
        self.duplicates = duplicates

        # now do import, ignoring duplicates
        to_import = sorted([(k, v) for k, v in raw_objects.items()
                            if k not in duplicates],
                           key=lambda i: getattr(i[1], 'parent_id', 0))

        for json_id, obj in to_import:
            # parentless objects come first, should mean they are in
            # self.json_to_db_id before their children need them so we can
            # resolve their id
            # XXX: known issue here if there are sub-subcommittees, it'll
            # result in an unresolvable id
            parent_id = getattr(obj, 'parent_id', None)
            if parent_id:
                obj.parent_id = self.resolve_json_id(parent_id)

            self.json_to_db_id[json_id] = self.import_object(obj)

        return {self._type: self.results}

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
        if not json_id:
            return None

        json_id = self.dedupe_json_id(json_id)

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
