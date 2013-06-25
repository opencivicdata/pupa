#!/usr/bin/env python
from pupa.utils import JSONEncoderPlus
from contextlib import contextmanager
from pymongo import Connection
import argparse
import json
import os

parser = argparse.ArgumentParser(description='Re-convert a jurisdiction.')
parser.add_argument('jurisdiction', type=str, help='jurisdiction_id to dump',
                    default=None, nargs='?')
parser.add_argument('--server', type=str, help='Mongo Server',
                    default="localhost")
parser.add_argument('--database', type=str, help='Mongo Database',
                    default="larvae")
parser.add_argument('--port', type=int, help='Mongo Server Port',
                    default=27017)
parser.add_argument('--output', type=str, help='Output Directory',
                    default="dump")

args = parser.parse_args()


@contextmanager
def cd(path):
    pop = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(pop)


connection = Connection(args.server, args.port)
db = getattr(connection, args.database)
jurisdiction = args.jurisdiction


def normalize_person(entry):
    data = list(db.memberships.find({
        "person_id": entry['_id']
    }))
    for datum in data:
        datum.pop('_id')

    entry['memberships'] = data

    return entry



def dump(collection, spec):
    for entry in collection.find(spec):
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
        #print path
        json.dump(entry, fd, cls=JSONEncoderPlus)


path = args.output
if not os.path.exists(path):
    os.makedirs(path)


def dump_people(where):
    orga = db.organizations.find_one({"jurisdiction_id": where,
                                      "classification": "jurisdiction"})
    if orga is None:
        raise Exception("Org came back none for %s" % (where))

    for membership in db.memberships.find({"organization_id": orga['_id']}):
        person = db.people.find_one({"_id": membership['person_id']})
        assert person is not None
        person = normalize_person(person)
        do_write(person, where=where)


def dump_juris(jurisdiction):
    spec = {"jurisdiction_id": jurisdiction}

    for collection in [
        db.bills,
        db.votes,
        db.events,
        db.organizations,
    ]:
        dump(collection, spec)

    dump_people(jurisdiction)


with cd(path):
    if jurisdiction:
        dump_juris(jurisdiction)
    else:
        for orga in db.organizations.find({
            "classification": "jurisdiction"
        }):
            if 'jurisdiction_id' not in orga:
                print "WARNING: NO JURISDICTION_ID ON %s" % (orga['_id'])
                continue

            dump_juris(orga['jurisdiction_id'])
