#!/usr/bin/env python
from pymongo import Connection

#SERVER = "ec2-184-73-58-184.compute-1.amazonaws.com"
SERVER = "localhost"
DATABASE = "ocd"


connection = Connection(SERVER, 27017)
db = getattr(connection, DATABASE)


_got = {}
def getorg(what):
    if what in _got:
        return _got.get(what)
    el = db.orgnizations.find_one({"_id": what})
    _got[what] = el
    return el

def getperson(what):
    if what in _got:
        return _got.get(what)
    el = db.people.find_one({"_id": what})
    _got[what] = el
    return el



def process_memberships():
    for membership in db.memberships.find():
        org = getorg(membership['organization_id'])
        who = getperson(membership['person_id'])
        has_org = False
        has_person = False

        if org:
            has_org = True

        if who:
            has_person = True

        id_ = membership['_id']
        if has_org and has_person:
            pass  # OK
        elif has_org:
            print id_, "No person."
        elif has_person:
            print id_, "No org."
            process_person(who)
        else:
            print id_, "Has neither"


def process_person(who):
    id_ = who['_id']
    n = db.memberships.find({"person_id": id_}).count()
    if n == 0:
        raise SanityException("This is insane")
    if n == 1:
        print "  --> Can remove."


process_memberships()
