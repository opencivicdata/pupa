from __future__ import print_function
from contextlib import contextmanager
import json
import os
from .base import BaseCommand
from pupa.utils import JSONEncoderPlus


@contextmanager
def cd(path):
    pop = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(pop)


def normalize_person(entry):
    data = list(db.memberships.find({
        "person_id": entry['_id']
    }, timeout=False))
    for datum in data:
        datum.pop('_id')

    entry['memberships'] = data

    return entry


def dump(collection, spec):
    for entry in collection.find(spec, timeout=False):
        do_write(entry)


def do_write(entry, where=None):
    path = entry['_id']

    if where is None:
        where = entry['jurisdiction_id']

    path = "%s/%s" % (where, path)
    basename = os.path.dirname(path)
    if not os.path.exists(basename):
        os.makedirs(basename)

    with open(path, 'w') as fd:
        json.dump(entry, fd, cls=JSONEncoderPlus)


def dump_people(where):
    iterated = False
    for orga in db.organizations.find({"jurisdiction_id": where,
                                       "classification": "legislature"}):
        iterated = True
        for membership in db.memberships.find({"organization_id": orga['_id']},
                                              timeout=False):
            person = db.people.find_one({"_id": membership['person_id']})
            assert person is not None
            person = normalize_person(person)
            do_write(person, where=where)

    if iterated is False:
        raise Exception("Org came back none for %s" % (where))


def dump_jurisdiction_data(where):
    meta = db.jurisdictions.find_one({"_id": where})
    if meta is None:
        return

    for x in [
        'latest_json_url', 'latest_csv_url',
        'latest_json_date', 'latest_csv_date'
    ]:
        if x in meta:
            meta.pop(x, None)

    for key in meta.keys():
        if key.startswith("_") and key != "_id":
            meta.pop(key)

    path = "%s/jurisdiction.json" % (meta['_id'])
    with open(path, 'w') as fd:
        json.dump(meta, fd, cls=JSONEncoderPlus)


def dump_juris(jurisdiction):
    spec = {"jurisdiction_id": jurisdiction}

    for collection in [db.bills, db.votes, db.events, db.organizations]:
        dump(collection, spec)

    dump_people(jurisdiction)
    dump_jurisdiction_data(jurisdiction)


class Command(BaseCommand):
    name = 'dump'
    help = '''create a json dump'''

    def add_args(self):
        self.add_argument('jurisdiction', type=str, help='jurisdiction_id to dump',
                          default=None, nargs='?')
        self.add_argument('--output', type=str, help='output directory', default="dump")

    def handle(self, args):
        path = args.output
        if not os.path.exists(path):
            os.makedirs(path)

        with cd(path):
            if args.jurisdiction:
                dump_juris(args.jurisdiction)
            else:
                for orga in db.organizations.find({
                    "classification": "legislature",
                }, timeout=False):
                    if 'jurisdiction_id' not in orga:
                        print("WARNING: NO JURISDICTION_ID ON %s" % (orga['_id']))
                        continue

                    dump_juris(orga['jurisdiction_id'])
