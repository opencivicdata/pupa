import sys
import re
import pprint
from uuid import uuid4
from hashlib import md5
from inspect import getmembers, ismethod
from collections import defaultdict, deque, Counter

from pymongo import MongoClient


client = MongoClient()

old = old_openstates = client['fiftystates']
new = new_openstates = client['openstates-pupa']


class Converted(object):
    '''A helper class to hold functions and data relating to a
    converted record.
    '''
    def __init__(self, doc, collection_name):
        self.new = doc
        openstates_id = doc['_openstates_id']
        collection = getattr(old_openstates, collection_name)
        self.old = collection.find_one(openstates_id)

    def old_values(self):
        return set(TypeVisitor().visit(self.old))

    def new_values(self):
        return set(TypeVisitor().visit(self.new))

    def run_checks(self):
        '''Run any specific checks defined on this collections subclass.
        '''
        for name, method in getmembers(self, ismethod):
            if name.startswith('check_'):
                method()

    def count_missing_keys(self, counter, ids):
        '''Compare the new and old documents. For an values in the old doc
        that are not present in the new doc, log the corresponding key
        paths and increment those paths in the counter.
        '''
        index = Index()
        object_id = self.old['_id']
        index.add_object(self.old, object_id)

        missing = self.old_values() - self.new_values()
        ignored_keys = getattr(self, 'ignored_keys', [])

        for value in missing:
            keypaths = index.keypaths_for_value(value, object_id)
            for path in map(scrub_keypath, keypaths):
                counter[path] += 1
                ids[path].add((self.new['_id'], self.old['_id']))


class ConvertedPerson(Converted):
    '''
    Old roles not copied over, except for role in chamber. In those,
    district and term not getting copied, though years of term are
    being copied over as start_date and end_date.

    Possibly legitimate:
     - roles.term: doesn't appear to have made it into memberships
     - roles.position: should probably end up on membership.role?
     - roles.chamber: not copied to membership, but still available on org
     - old_roles.district: not getting copied to historic chamber membership?
     - old_roles.term: not getting copied to historic chamber membership?
     - offices.(type,phone,name,fax)
     - active: guessing not part of new schema
     - _locked_fields: probably want these?
     - _scraped_name: same?

    These ones not getting copied to extras. Intentional?
     - _contributions_start_year: 955,
     - _total_contributions: 901,
     - _yearly_contributions': 6549,

    False negatives:
     - _all_ids: replaced by identifiers dict
     - email: empty strings not copied
     - middle_name: not in new schema
     - nickname: empty strings not copied
     - photo_url: empty strings not copied
     - suffixes: empty strings not copied
     - transparencydata_id: empty strings not copied
     - roles.subcommittee: usually empty string, and replaced with parent/child orgs
     - roles.state: --> memb.org.division_id
     - roles.committee_id --> memb.org_id
     - roles.committee --> memb.org.name
     - roles.state --> memb.org.jurisdiction_id?
     - roles.party -> memb.org.name
     - roles.type --> implicit in membership collection name?
    '''

    def __init__(self, doc, collection_name):
        self.new = doc
        openstates_id = doc['_openstates_id']
        self.old = old_openstates.legislators.find_one(openstates_id)


class ConvertedEvent(Converted):
    '''This class isn't actually used--just documenting results here.

    Possibly legitimate:
    - type: should be getting copied over as 'committee:hearing', not 'event'
    - timezone: not getting copied
    - related_bills: not getting copied
    - notes: note getting copied
    - participants: sometimes, everything gets copied. Other looks like
      nothing gets copied (see 'ocd-event/0ad19292-fab6-11e2-a853-f0def1bd785e', 'ARE00000767')
    - link: this field on old events was the event detail page. Should probably
      end up in 'sources' dict on new events.
    -

    Do we care about plus fields and underscore fields? Not copied:
    - documents.+mimetype: not getting copied
    - documents.+type: not getting copied
    - _ical_feed
    - _guid
    - +chamber
    - +location_url

    False Negatives:
    - state --> jurisdiction_id
    - level --> jurisdiction_id
    - country --> jurisdiction_id
    '''

class ConvertedBill(Converted):
    '''
    Possibly legitimate:
    - chamber: very small percentage are 'None'; see ('ocd-bill/98652a36-fac2-11e2-a853-f0def1bd785e', 'IAB00003060')
    -

    False negatives:
    - action_dates.*: only used for openstates? Not sure about this one.
      May be important for certain queries.
    - actions.+*: lots of random plus fields.
    - actions.related_entities.id --> correctly changed to OCD ids
    - actions.related_entities.type --> correctly changed from 'committee'
      to 'organization'
    - country --> jurisdiction_id
    -
    '''
    def check_all_ids(self):
        '''Make sure _all_ids gets correctly copied.
        '''
        identifiers = list(self.new['identifiers'])
        for _id in self.old['_all_ids']:
            for data in identifiers:
                if data == dict(identifier=_id, scheme='openstates'):
                    identifiers.remove(data)
        assert identifiers == []

    def check_chamber(self):
        assert self.new['chamber'] == self.old['chamber']


class ConvertedVote(Converted):
    '''
    Possibly legitimate:
    - bill_chamber: get copied to bill.chamber (currently None) i.e., 'ocd-vote/bc60ab4a-fac2-11e2-a853-f0def1bd785e'
    - sources.retrieved: large number of bills have this timestamp in sources dicts--not getting copied
    - committee: set to the committee name on some votes--not getting copied
    - committee_id: small number of bills have this--not copied

    False negatives:
    - date: string in new database, timestampy in old.
    - state --> division_id
    - other_votes.leg_id --> using ocd ids instead.
    - no_votes.leg_id --> using ocd ids instead.
    - yes_votes.leg_id --> using ocd ids instead.
    '''


#---------------------------------------------------------------
# Visitor plumbing.
class Visitor(object):
    '''Visitor base.
    '''
    def __init__(self):
        self.deque = deque()

    def visit(self, obj):
        self.obj = obj
        self.visit_node(obj)
        return self.finalize()

    def visit_node(self, obj):
        '''Visit a single node.
        '''
        name = obj.__class__.__name__
        method = getattr(self, 'visit_' + name, None)
        if method is not None:
            return method(obj)
        else:
            return self.generic_visit(obj)

    def generic_visit(self, obj):
        '''Default visit function if none defined for the object's type.
        '''
        self.deque.appendleft(obj)

    def finalize(self):
        '''Final steps the visitor needs to take, plus the
        return value or .visit, if any.
        '''
        return self.deque


class TypeVisitor(Visitor):
    '''Visit each part of a dictionary with arbitrarily nested data.
    Do something specefic for each type of data encountered.
    '''
    def visit_dict(self, obj):
        for key, value in obj.items():
            self.visit_node(value)

    def visit_list(self, obj):
        for element in obj:
            self.visit_node(element)


# -------------------------------------------------------------
# Splunk-style in-memory index of an object.
class IndexEntry(object):
    '''Class the inspects a dictionary and yields tuples of
    values and keypaths for creating an index.
    '''
    def __init__(self, obj):
        self.obj = obj

    def _handle_value(self, value, pathsegs=None):
        pathsegs = list(pathsegs or [])
        if isinstance(value, dict):
            yield from self._generate_obj_items(value, pathsegs)
        elif isinstance(value, (list, tuple, set)):
            yield from self._generate_list_items(value, pathsegs)
        else:
            yield ('.'.join(pathsegs), value)

    def _generate_obj_items(self, obj, pathsegs=None):
        pathsegs = list(pathsegs or [])
        for key, value in obj.items():
            _pathsegs = pathsegs[:]
            _pathsegs.append(key)
            yield from self._handle_value(value, _pathsegs)

    def _generate_list_items(self, obj, pathsegs=None):
        pathsegs = list(pathsegs or [])
        for key, value in enumerate(obj):
            _pathsegs = pathsegs[:]
            _pathsegs.append(str(key))
            yield from self._handle_value(value, _pathsegs)

    def __iter__(self):
        yield from self._handle_value(self.obj)


class _IndexMaps(object):
    '''Helper to hold the index dictionaries.
    '''
    def __init__(self):
        self.keypath_value_id = defaultdict(lambda: defaultdict(list))
        self.value_id_keypath = defaultdict(lambda: defaultdict(list))
        self.values = {}


class Index(object):
    '''Main index object and helper methods.
    '''
    def __init__(self):
        self.maps = _IndexMaps()

    def _add_item(self, object_id, keypath, value):
        value_id = md5(str(value).encode('utf-8')).hexdigest()

        # Maps [keypath][value_id] to a list of object ids.
        self.maps.keypath_value_id[keypath][value_id].append(object_id)

        # Maps [value_id][object_id] to a list of keypaths.
        self.maps.value_id_keypath[value_id][object_id].append(keypath)

        # Map value_id to its value.
        self.maps.values[value_id] = value

    def add_object(self, obj, object_id=None):
        if object_id is None:
            object_id = str(uuid4())
        for item in IndexEntry(obj):
            self._add_item(object_id, *item)

    def show_keys(self):
        for key, val in self.maps.keypath_value_id.items():
            print(key, len(val))

    def keypaths_for_value(self, value, object_id=None):
        '''Given a value, retrieve all dict of object_ids, each mapping
        to a list of keypaths that end in that value.
        '''
        value_id = md5(str(value).encode('utf-8')).hexdigest()
        res = self.maps.value_id_keypath[value_id]
        if object_id is None:
            return res
        else:
            return res[object_id]


if __name__ == '__main__':


    re_keypath = re.compile(r'\.\d+')
    def scrub_keypath(path):
        '''Remove integers in keypaths.
        '''
        return re_keypath.sub('', path)

    class Result(dict):
        def __missing__(self, collection_name):
            value = {
                'counts': Counter(),
                'ids': defaultdict(set)
                }
            self[collection_name] = value
            return value

    result = Result()

    collections = sys.argv[1:] or ('bills', 'events', 'people', 'votes')

    class_map = dict(
        bills=ConvertedBill,
        events=ConvertedEvent,
        votes=ConvertedVote)

    # Bills and events----------------------------------------------------
    for collection_name in set(collections) - set(['people']):

        cls = class_map[collection_name]

        if collection_name not in collections:
            continue

        counter = result[collection_name]['counts']
        ids = result[collection_name]['ids']

        for doc in getattr(new, collection_name).find():#.limit(10000):
            bill = cls(doc, collection_name)
            bill.count_missing_keys(counter, ids)
            bill.run_checks()

    # Legislators ---------------------------------------------------------
    if 'people' in collections:
        orgs = {}
        for org in new.organizations.find():
            orgs[org['_id']] = org

        memberships = defaultdict(list)
        for memb in new.memberships.find():
            memberships[memb['person_id']].append(memb)

        counter = result['people']['counts']
        ids = result['people']['ids']

        for person in new.people.find().limit(1000):
            membs = memberships[person['_id']]
            for memb in membs:
                memb['org'] = orgs[memb['organization_id']]
            person['memberships_data'] = membs
            person = ConvertedPerson(person, 'people')
            person.count_missing_keys(counter, ids)

    for collection_name in ('bills', 'people', 'events', 'votes'):
        if collection_name not in result:
            continue
        print('*' * 80)
        print(collection_name)
        pprint.pprint(dict(result[collection_name]['counts']))

    import pdb; pdb.set_trace()


