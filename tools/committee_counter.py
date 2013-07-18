#!/usr/bin/env

from pupa.core import db


for orga in db.organizations.find({"classification": "committee"}):
    memberships = db.memberships.find({
        "organization_id": orga['_id'],
        "end_date": None
    })

    print (memberships.count(),
           orga['_id'],
           orga['jurisdiction_id'],
           orga['name'].encode('utf-8'))

    for membership in memberships:
        mid = membership['person_id']
        print "    ", mid
        print membership
        person = db.people.find_one({"_id": mid})
        if person:
            print "        ", person['name']
