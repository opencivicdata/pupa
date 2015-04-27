import os
import copy
import glob
import json
import uuid
import logging
import datetime
from pupa.exceptions import DuplicateItemError
from pupa.utils import get_pseudo_id
from pupa.utils.topsort import Network
from opencivicdata.models import LegislativeSession
from pupa.exceptions import UnresolvedIdError, DataImportError


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


def items_differ(jsonitems, dbitems, subfield_dict):
    """ check whether or not jsonitems and dbitems differ """

    # short circuit common cases
    if len(jsonitems) == len(dbitems) == 0:
        # both are empty
        return False
    elif len(jsonitems) != len(dbitems):
        # if lengths differ, they're definitely different
        return True

    jsonitems = copy.deepcopy(jsonitems)
    keys = jsonitems[0].keys()

    # go over dbitems looking for matches
    for dbitem in dbitems:
        match = None
        for i, jsonitem in enumerate(jsonitems):
            # check if all keys (excluding subfields) match
            for k in keys:
                if k not in subfield_dict and getattr(dbitem, k) != jsonitem.get(k, None):
                    break
            else:
                # all fields match so far, possibly equal, just check subfields now
                for k in subfield_dict:
                    jsonsubitems = jsonitem[k]
                    dbsubitems = list(getattr(dbitem, k).all())
                    if items_differ(jsonsubitems, dbsubitems, subfield_dict[k][2]):
                        break
                else:
                    # these items are equal, so let's mark it for removal
                    match = i
                    break

        if match is not None:
            # item exists in both, remove from jsonitems
            jsonitems.pop(match)
        else:
            # exists in db but not json
            return True

    # if we get here, jsonitems has to be empty because we asserted that the length was
    # the same and we found a match for each thing in dbitems, here's a safety check just in case
    if jsonitems:       # pragma: no cover
        return True

    return False


class BaseImporter(object):
    """ BaseImporter

    Override:
        get_object(data)
        limit_spec(spec)                [optional, required if pseudo_ids are used]
        prepare_for_db(data)            [optional]
        postimport()                    [optional]
    """
    _type = None
    model_class = None
    related_models = {}
    preserve_order = set()

    def __init__(self, jurisdiction_id):
        self.jurisdiction_id = jurisdiction_id
        self.json_to_db_id = {}
        self.duplicates = {}
        self.pseudo_id_cache = {}
        self.session_cache = {}
        self.logger = logging.getLogger("pupa")
        self.info = self.logger.info
        self.debug = self.logger.debug
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.critical = self.logger.critical

    def get_session_id(self, identifier):
        if identifier not in self.session_cache:
            self.session_cache[identifier] = LegislativeSession.objects.get(
                identifier=identifier, jurisdiction_id=self.jurisdiction_id).id
        return self.session_cache[identifier]

    # no-ops to be overriden
    def prepare_for_db(self, data):
        return data

    def postimport(self):
        pass

    def resolve_json_id(self, json_id,data=None):
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

        if json_id.startswith('~'):
            # keep caches of all the pseudo-ids to avoid doing 1000s of lookups during import
            if json_id not in self.pseudo_id_cache:
                spec = get_pseudo_id(json_id)
                spec = self.limit_spec(spec)
                try:
                    self.pseudo_id_cache[json_id] = self.model_class.objects.get(**spec).id
                except self.model_class.DoesNotExist:
                    raise UnresolvedIdError('cannot resolve pseudo id to {}: {}.\nFull data: {}'.format(
                        self.model_class.__name__, json_id, data))
                except self.model_class.MultipleObjectsReturned:
                    raise UnresolvedIdError('multiple objects returned for pseudo id to {}: {}.\nFull data:'.format(
                        self.model_class.__name__, json_id, data))

            # return the cached object
            return self.pseudo_id_cache[json_id]

        # get the id that the duplicate points to, or use self
        json_id = self.duplicates.get(json_id, json_id)

        try:
            return self.json_to_db_id[json_id]
        except KeyError:
            raise UnresolvedIdError('cannot resolve id: {}'.format(json_id))

    def import_directory(self, datadir):
        """ import a JSON directory into the database """

        def json_stream():
            # load all json, mapped by json_id
            for fname in glob.glob(os.path.join(datadir, self._type + '_*.json')):
                with open(fname) as f:
                    yield json.load(f)

        return self.import_data(json_stream())

    def _prepare_imports(self, dicts):

        """ filters the import stream to remove duplicates

        also serves as a good place to override if anything special has to be done to the
        order of the import stream (see OrganizationImporter)
        """
        # hash(json): id
        seen_hashes = {}

        for data in dicts:
            json_id = data.pop('_id')

            # map duplicates (using omnihash to tell if json dicts are identical-ish)
            objhash = omnihash(data)
            if objhash not in seen_hashes:
                seen_hashes[objhash] = json_id
                yield json_id, data
            else:
                self.duplicates[json_id] = seen_hashes[objhash]

    def import_data(self, data_items):
        """ import a bunch of dicts together """
        # keep counts of all actions
        record = {
            'insert': 0, 'update': 0, 'noop': 0,
            'start': datetime.datetime.utcnow(),
        }

        for json_id, data in self._prepare_imports(data_items):
            obj_id, what = self.import_item(data)
            self.json_to_db_id[json_id] = obj_id
            record[what] += 1

        # all objects are loaded, a perfect time to do inter-object resolution and other tasks
        self.postimport()

        record['end'] = datetime.datetime.utcnow()

        return {self._type: record}

    def import_item(self, data):
        """ function used by import_data """
        what = 'noop'

        # remove the JSON _id (may still be there if called directly)
        data.pop('_id', None)

        # add fields/etc.
        data = self.prepare_for_db(data)

        try:
            obj = self.get_object(data)
        except self.model_class.DoesNotExist:
            obj = None

        # pull related fields off
        related = {}
        for field in self.related_models:
            related[field] = data.pop(field)

        # obj existed, check if we need to do an update
        if obj:
            if obj.id in self.json_to_db_id.values():
                raise DuplicateItemError(data, obj)
            # check base object for changes
            for key, value in data.items():
                if getattr(obj, key) != value:
                    setattr(obj, key, value)
                    what = 'update'
            if what == 'update':
                obj.save()

            updated = self._update_related(obj, related, self.related_models)
            if updated:
                what = 'update'

        # need to create the data
        else:
            what = 'insert'
            try:
                obj = self.model_class.objects.create(**data)
            except TypeError as e:
                raise DataImportError('{} while importing {} as {}'.format(e, data,
                                                                           self.model_class))
            self._create_related(obj, related, self.related_models)

        return obj.id, what



    def _update_related(self, obj, related, subfield_dict):
        """
        update DB objects related to a base object
            obj:            a base object to create related
            related:        dict mapping field names to lists of related objects
            subfield_list:  where to get the next layer of subfields
        """
        # keep track of whether or not anything was updated
        updated = False

        # for each related field - check if there are differences
        for field, items in related.items():
            # get items from database
            dbitems = list(getattr(obj, field).all())
            dbitems_count = len(dbitems)

            # default to doing nothing
            do_delete = do_update = False

            if items and dbitems_count:         # we have items, so does db, check for conflict
                do_delete = do_update = items_differ(items, dbitems, subfield_dict[field][2])
            elif items and not dbitems_count:   # we have items, db doesn't, just update
                do_update = True
            elif not items and dbitems_count:   # db has items, we don't, just delete
                do_delete = True
            # otherwise: no items or dbitems, so nothing is done

            if do_delete:
                updated = True
                getattr(obj, field).all().delete()
            if do_update:
                updated = True
                self._create_related(obj, {field: items}, subfield_dict)

        return updated

    def _create_related(self, obj, related, subfield_dict):
        """
        create DB objects related to a base object
            obj:            a base object to create related
            related:        dict mapping field names to lists of related objects
            subfield_list:  where to get the next layer of subfields
        """
        for field, items in related.items():
            subobjects = []
            all_subrelated = []
            Subtype, reverse_id_field, subsubdict = subfield_dict[field]
            for order, item in enumerate(items):
                # pull off 'subrelated' (things that are related to this obj)
                subrelated = {}
                for subfield in subsubdict:
                    subrelated[subfield] = item.pop(subfield)

                if field in self.preserve_order:
                    item['order'] = order

                item[reverse_id_field] = obj.id

                try:
                    subobjects.append(Subtype(**item))
                    all_subrelated.append(subrelated)
                except Exception as e:
                    raise DataImportError('{} while importing {} as {}'.format(e, item, Subtype))

            # add all subobjects at once (really great for actions & votes)
            try:
                Subtype.objects.bulk_create(subobjects)
            except Exception as e:
                raise DataImportError('{} while importing {} as {}'.format(e, subobjects, Subtype))

            # after import the subobjects, import their subsubobjects
            for subobj, subrel in zip(subobjects, all_subrelated):
                self._create_related(subobj, subrel, subsubdict)
