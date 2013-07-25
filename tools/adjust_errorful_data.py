#!/usr/bin/env python

import sys
import json
import argparse
import datetime
from pymongo import Connection

parser = argparse.ArgumentParser(description='Check an OCD Database.')
parser.add_argument('--server', type=str, help='OCD Mongo Server',
                    default="localhost")
parser.add_argument('--database', type=str, help='OCD Mongo Database',
                    default="ocd")
parser.add_argument('--port', type=int, help='OCD Mongo Server Port',
                    default=27017)
parser.add_argument("--write-data", type=bool, help='dont write changes',
                    default=False)
parser.add_argument('file', type=str, help='Scruffy Report JSON file',
                    default='report.json')

args = parser.parse_args()

connection = Connection(args.server, args.port)
db = getattr(connection, args.database)


fatal_errors = [
    "event-has-unlinked-jurisdiction-id",
    "vote-has-unlinked-jurisdiction-id",
]


with open(args.file, mode='r') as fd:
    data = json.load(fd)


for collection, entries in data.items():
    cdb = getattr(db, collection)
    if not args.write_data:
        def fake_save(obj):
            print " .. would have written %s" % (obj['_id'])

        def fake_remove(obj):
            print " .. would have removed %s" % (obj['_id'])

        cdb.save = fake_save
        cdb.remove = fake_remove

    for datum in entries:
        if datum['tagname'] in fatal_errors:
            cdb.remove(datum['id'], safe=True)
            print datum['id'], "removed"

        indt = lambda x: not isinstance(x, datetime.datetime)

        if datum['tagname'] == 'start-is-not-datetime':
            event = cdb.find_one({"_id": datum['id']})
            if event is None:
                continue

            if indt(event['when']):
                event['when'] = datetime.datetime.fromtimestamp(event['when'])
                cdb.save(event)

        if datum['tagname'] == 'end-is-not-datetime':
            event = cdb.find_one({"_id": datum['id']})
            if event is None:
                continue
            if indt(event['end']):
                event['end'] = datetime.datetime.fromtimestamp(event['end'])
                cdb.save(event)

        if datum['tagname'] == 'membership-without-any-relation':
            cdb.remove(datum['id'], safe=True)

        if datum['tagname'] == 'bad-sponsor-id':
            one = cdb.find_one({"_id": datum['id']})
            if one is None:
                continue

            bsid = datum['data']['id']

            for sponsor in one['sponsors']:
                if sponsor['id'] == bsid:
                    sponsor['id'] = None
                    print one['_id'], "removed bad sponsor"
            cdb.save(one)

        if datum['tagname'] == 'bad-related-entity':
            one = cdb.find_one({"_id": datum['id']})
            if one is None:
                continue

            bsid = datum['data']['id']

            for item in one['agenda']:
                for who in item['related_entities']:
                    if who['id'] == bsid:
                        who['id'] = None
                        print one['_id'], "removed bad relation"
            cdb.save(one)
