#!/usr/bin/env python

import json
import sys
from pupa.core import db


fatal_errors = [
    "event-has-unlinked-jurisdiction-id",
    "vote-has-unlinked-jurisdiction-id",
]


with open(*sys.argv[1:], mode='r') as fd:
    data = json.load(fd)


for collection, entries in data.items():
    cdb = getattr(db, collection)
    for datum in entries:
        if datum['tagname'] in fatal_errors:
            cdb.remove(datum['id'], safe=True)
            print datum['id'], "removed"

        if datum['tagname'] == 'bad-sponsor-id':
            one = cdb.find_one({"_id": datum['id']})
            if one is None:
                continue

            bsid = datum['data']['sponsor-id']

            for sponsor in one['sponsors']:
                if sponsor['id'] == bsid:
                    sponsor['id'] = None
                    print one['_id'], "removed bad sponsor"
            cdb.save(one)
