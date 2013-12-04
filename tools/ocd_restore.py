#!/usr/bin/env python
from pupa.utils import JSONEncoderPlus
from contextlib import contextmanager
from pymongo import Connection
import argparse
import json
import sys
import os

parser = argparse.ArgumentParser(description='Re-convert a jurisdiction.')

parser.add_argument('--server', type=str, help='Mongo Server',
                    default="localhost")

parser.add_argument('--database', type=str, help='Mongo Database',
                    default="opencivicdata")

parser.add_argument('--port', type=int, help='Mongo Server Port',
                    default=27017)

parser.add_argument('--output', type=str, help='Output Directory',
                    default="dump")

parser.add_argument('root', type=str, help='root', default='dump')

args = parser.parse_args()


connection = Connection(args.server, args.port)
db = getattr(connection, args.database)


TABLES = {
    "ocd-jurisdiction": db.jurisdictions,
    "ocd-bill": db.bills,
    "ocd-organization": db.organizations,
    "ocd-person": db.people,
    "ocd-vote": db.votes,
}


@contextmanager
def cd(path):
    pop = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(pop)


def insert(obj):
    id_ = obj['_id']
    etype, _ = id_.split("/", 1)
    sys.stdout.write(etype.split("-")[1][0].lower())
    sys.stdout.flush()
    return TABLES[etype].save(obj)


with cd(args.root):
    # OK. Let's load stuff up.
    for path, dirs, nodes in os.walk("."):
        for entry in (os.path.join(path, x) for x in nodes):
            data = json.load(open(entry, 'r'))
            insert(data)
