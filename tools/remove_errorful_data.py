#!/usr/bin/env python

import json
import sys
from pupa.core import db


fatal_errors = [
    "event-has-invalid-jurisdiction-id",
    "vote-has-invalid-jurisdiction-id",
]


with open(*sys.argv[1:], mode='r') as fd:
    data = json.load(fd)


for collection, entries in data.items():
    for datum in entries:
        if datum['tagname'] in fatal_errors:
            getattr(db, collection).remove(datum['id'], safe=True)
            print datum['id'], "removed"
