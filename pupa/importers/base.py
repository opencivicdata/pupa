import os
import glob
import json
import uuid
import logging
from django.db.models import Model
from pupa.utils.topsort import Network


def omnihash(obj):
    """ recursively hash unhashable objects """
    if isinstance(obj, set):
        return hash(frozenset(omnihash(e) for e in obj))
    elif isinstance(obj, (tuple, list)):
        return hash(tuple(omnihash(e) for e in obj))
    elif isinstance(obj, dict):
        return hash(frozenset((k, omnihash(v)) for k, v in obj.items()))
    else:
        return hash(obj)


class BaseImporter(object):
    """ BaseImporter

    Override:
        prepare_for_db(data) [optional]
        get_object(data)
    """
    _type = None
    model_class = None
    related_models = {}

    def __init__(self, jurisdiction_id):
        self.jurisdiction_id = jurisdiction_id
        self.results = {'insert': 0, 'update': 0, 'noop': 0}
        self.json_to_db_id = {}
        self.duplicates = {}
        self.logger = logging.getLogger("pupa")
        self.info = self.logger.info
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical

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

        # get the id that the duplicate points to, or use self
        json_id = self.duplicates.get(json_id, json_id)

        try:
            return self.json_to_db_id[json_id]
        except KeyError:
            raise ValueError('cannot resolve id: {0}'.format(json_id))

    def prepare_for_db(self, data):
        # no-op to be overridden
        return data

    def import_directory(self, datadir):
        """ import a JSON directory into the database """
        dicts = []

        # load all json, mapped by json_id
        for fname in glob.glob(os.path.join(datadir, self._type + '_*.json')):
            with open(fname) as f:
                dicts.append(json.load(f))

        self.import_data(dicts)

    def import_data(self, dicts):
        """ import a bunch of dicts together """
        # id: json
        data_by_id = {}
        # hash(json): id
        seen_hashes = {}

        # load all json, mapped by json_id
        for data in dicts:
            json_id = data.pop('_id')
            objhash = omnihash(data)
            if objhash not in seen_hashes:
                seen_hashes[objhash] = json_id
                data_by_id[json_id] = data
            else:
                self.duplicates[json_id] = seen_hashes[objhash]

        # toposort the nodes so parents are imported first
        network = Network()
        in_network = set()
        import_order = []

        for json_id, data in data_by_id.items():
            parent_id = data.get('parent_id', None)
            network.add_node(json_id)
            if parent_id:
                # Right. There's an import dep. We need to add the edge from
                # the parent to the current node, so that we import the parent
                # before the current node.
                network.add_edge(parent_id, json_id)

        # resolve the sorted import order
        for jid in network.sort():
            import_order.append((jid, data_by_id[jid]))
            in_network.add(jid)

        # ensure all data made it into network
        if in_network != set(data_by_id.keys()):
            raise Exception("import is missing nodes in network set")

        # time to actually do the import
        for json_id, data in import_order:
            parent_id = data.get('parent_id', None)
            if parent_id:
                # If we've got a parent ID, let's resolve it's JSON id
                # (scrape-time) to a Database ID (needs to have had the
                # parent imported first - which we asserted is true via
                # the topological sort)
                data['parent_id'] = self.resolve_json_id(parent_id)
            obj, what = self._import_item(data)
            self.json_to_db_id[json_id] = obj.id
            self.results[what] += 1

        return {self._type: self.results}

    def _import_item(self, data):
        """ internal function used by import_data """
        what = None
        updated = False

        # add fields/etc.
        data = self.prepare_for_db(data)

        # TODO: add a JSON field for extras
        data.pop('extras', None)

        try:
            obj = self.get_object(data)
        except self.model_class.DoesNotExist:
            obj = None

        # pull related fields off
        related = {}
        for field in self.related_models:
            related[field] = data.pop(field)

        # obj existed, attempt to update
        if obj:
            for key, value in data.items():
                # TODO: avoid updating locked fields
                if getattr(obj, key) != value:
                    setattr(obj, key, value)
                    updated = True

            if updated:
                obj.save()
                what = 'update'
            else:
                what = 'noop'

            # for each related field - check if there are notable differences
            for field, items in related.items():
                if items:
                    # get keys to compare (assumes all objects have same keys)
                    keys = sorted(items[0].keys())

                    # get items from database
                    dbitems = getattr(obj, field).all()
                    dbdicts = [{k: getattr(item, k) for k in keys} for item in dbitems]
                    # if the hashes differ, update what & delete existing set, then replace it
                    if omnihash(items) != omnihash(dbdicts):
                        what = 'update'
                        getattr(obj, field).all().delete()
                        for item in items:
                            try:
                                getattr(obj, field).create(**item)
                            except TypeError as e:
                                raise TypeError(str(e) + ' while importing ' + str(item))

        # need to create the data
        else:
            what = 'insert'
            if 'id' not in data:
                data['id'] = 'ocd-{0}/{1}'.format(self._type, uuid.uuid1())
            obj = self.model_class.objects.create(**data)

            self._create_related(obj, related)

        return obj, what


    def _create_related(self, obj, related, subfield_dict=None):
        # obj is a base object to create related
        # related is a dict mapping field names to lists of related objects
        # subfield_list is where to get the next layer of subfields
        if not subfield_dict:
            subfield_dict = self.related_models

        # for each field add related
        for field, items in related.items():
            for item in items:

                # pull off 'subrelated' (things that are related to this obj)
                subrelated = {}
                for subfield in subfield_dict[field]:
                    subrelated[subfield] = item.pop(subfield)

                try:
                    subobj = getattr(obj, field).create(**item)
                except TypeError as e:
                    raise TypeError(str(e) + ' while importing ' + str(item))

                self._create_related(subobj, subrelated, subfield_dict[field])
