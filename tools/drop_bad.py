#!/usr/bin/env python
from pymongo import Connection


connection = Connection('localhost', 27017)
db = getattr(connection, 'pupa')


def purge_org(org):
    for membership in db.memberships.find({"organization_id": org}):
        who = db.people.find_one({"_id": membership['person_id']})
        if who:
            db.people.remove({"_id": who['_id']})
        db.memberships.remove({"_id": membership['_id']})

    for sub in db.organizations.find({"parent_id": org}):
        purge_org(sub)
    db.organizations.remove({"_id": org})


for org in [
    "us-ma-bos", "us-id-boise", "us-nc-car", "us-oh-cle",
    "us-ny-nyc", "us-pa-philadelphia", "us-nm-roswell", "us-nm-saf",
    "us-ca-temecula"
]:
    for o in db.organizations.find({"jurisdiction_id": org}):
        purge_org(o['_id'])

    db.votes.remove({"jurisdiction_id": org})
    db.events.remove({"jurisdiction_id": org})
    db.bills.remove({"jurisdiction_id": org})
    db.metadata.remove({"_id": org})
