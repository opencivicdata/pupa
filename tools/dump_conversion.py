#!/usr/bin/env python
from pupa.utils import JSONEncoderPlus
from pymongo import Connection
import json
import os



SERVER = "ec2-184-73-58-184.compute-1.amazonaws.com"
DATABASE = "ocd"

connection = Connection(SERVER, 27017)
db = getattr(connection, DATABASE)


def dump(jurisdiction, obj):
    path = "%s/%s" % (jurisdiction, obj['_id'])
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    json.dump(obj, open(path, 'w'), cls=JSONEncoderPlus)


def dump_person(who, jurisdiction):
    obj = db.people.find_one({"_id": who})
    obj['memberships'] = list(db.memberships.find({"person_id": who}))
    for membership in obj['memberships']:
        membership.pop("_id")
        if 'jurisdiction' in membership:
            membership.pop("jurisdiction")
    dump(jurisdiction, obj)


def dump_suborg(what, jurisdiction):
    for org in db.organizations.find({"parent_id": what}):
        dump(jurisdiction, org)
        dump_suborg(org['_id'], jurisdiction)


def dump_bills(abbr, jurisdiction, key='jurisdiction_id'):
    for bill in db.bills.find({key: abbr}):
        dump(jurisdiction, bill)


def dump_votes(abbr, jurisdiction, key='jurisdiction_id'):
    for vote in db.votes.find({key: abbr}):
        dump(jurisdiction, vote)


def dump_events(abbr, jurisdiction, key='jurisdiction_id'):
    for event in db.events.find({key: abbr}):
        dump(jurisdiction, event)


def dump_org(what, jurisdiction):
    org = db.organizations.find_one({"_id": what})
    print org['name']
    dump(jurisdiction, org)

    dump_suborg(what, jurisdiction)
    for membership in db.memberships.find({"organization_id": what}):
        dump_person(membership['person_id'], jurisdiction)

    kwargs = {}
    abbr = None
    if org.get('openstates_id'):
        abbr = org['openstates_id']
        assert len(abbr) == 2
        kwargs['key'] = "jurisdiction"
    elif org.get('jurisdiction_id'):
        abbr = org['jurisdiction_id']
    else:
        return

    if abbr is None:
        raise Exception

    dump_bills(abbr, jurisdiction, **kwargs)
    dump_votes(abbr, jurisdiction, **kwargs)
    dump_events(abbr, jurisdiction, **kwargs)


for org in db.organizations.find({"$or": [{"classification": "jurisdiction"}, {"classification": {"$exists": False}}]}):
    dump_org(org['_id'], org['_id'])
