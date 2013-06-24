#!/usr/bin/env python

"""
OK. Let's spot-check a few bills.

"""

from billy.core import db
from pymongo import Connection

connection = Connection('localhost', 27017)
nudb = connection.larvae  # XXX: Fix the db name


pdb = nudb.people


def check_people():
    print "Checking people"
    for person in pdb.find():
        pid, osid = (person.get(x) for x in ('_id', 'openstates_id'))
        refobj = db.legislators.find_one({"_id": osid})
        assert refobj is not None  # OK. We have a valid backref.

        memberships = nudb.memberships.find({"person_id": pid})
        has_juris = False
        has_party = False

        for membership in memberships:
            orgid = membership['organization_id']
            orga = nudb.organizations.find_one({"_id": orgid})
            assert orga is not None
            klass = orga['classification']
            if klass == 'party':
                has_party = True
            if klass == 'jurisdiction':
                assert has_juris is False
                has_juris = True
                # validate state
        assert has_juris, has_party


def check_bills():
    print "Checking bills"
    for bill in nudb.bills.find():
        osbill = db.bills.find_one({"_id": bill['openstates_id']})
        for sponsor in bill['sponsors']:
            ocdid = sponsor.get('id', None)
            if ocdid is None:
                continue

            who = None
            type_ = sponsor['_type']
            if type_ == 'organization':
                who = nudb.organizations.find_one({"_id": ocdid})
            if type_ == 'person':
                who = pdb.find_one({"_id": ocdid})

            assert who

        oactions = [x['description'] for x in bill['actions']]
        for action in osbill['actions']:
            assert action['action'] in oactions


def check_events():
    print "Checking events"
    for event in nudb.events.find():
        osevent = db.events.find_one({"_id": event['openstates_id']})
        fkname = [x['participant'] for x in osevent['participants']]

        for whom in event['participants']:
            assert whom['name'] in fkname

        for thing in osevent.get('related_bills', []):
            pass

        info = filter(lambda x: x is not None,
                      [x.get('bill_id', None) for x
                       in osevent.get('related_bills', [])])

        for item in event['agenda']:
            for entity in item['related_entities']:
                assert entity['name'] in info

        assert osevent
        assert osevent['when'] == event['when']
        assert osevent.get('end') == event.get('end')


check_events()
check_bills()
check_people()
