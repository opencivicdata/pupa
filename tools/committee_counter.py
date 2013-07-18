#!/usr/bin/env

from pupa.core import db


for orga in db.organizations.find({"classification": "committee"}):
    memberships = db.memberships.find({
        "organization_id": orga['_id'],
        "end_date": None
    }).count()
    print memberships, orga['jurisdiction_id'], orga['name']
