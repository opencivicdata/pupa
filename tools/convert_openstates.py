#!/usr/bin/env python

from larvae.organization import Organization
from larvae.membership import Membership
from larvae.person import Person
from larvae.event import Event
from larvae.vote import Vote
from larvae.bill import Bill

from pymongo import Connection
import datetime as dt
import uuid
import sys


QUIET = True


type_tables = {
    Organization: "organizations",
    Membership: "memberships",
    Person: "people",
    Bill: "bills",
    Event: "events",
    Vote: "votes",
}

_hot_cache = {}
_cache_touched = {}


def obj_to_jid(obj):
    abbr = None
    if obj.openstates_id:
        abbr = obj.openstates_id[:2]

    if abbr is None:
        raise Exception("Can't auto-detect the Jurisdiction ID")

    abbr = abbr.lower()
    jid = "ocd-jurisdiction/country:us/state:%s/legislature" % (abbr)
    return jid



def load_hot_cache(state):
    spec = {}
    if state:
        spec['state'] = state
    #print "Loading cache"
    for entry in nudb.openstates_cache.find(spec):
        _hot_cache[entry['_id']] = entry['ocd-id']
    #print "Cache loaded"


def write_hot_cache(state):
    global _cache_touched
    #print "Writing cache"
    for entry in _hot_cache:
        if entry is None:
            continue

        if _cache_touched.get(entry, False):
            nudb.openstates_cache.update({"_id": entry},
                                         {"_id": entry,
                                          "state": entry[:2].lower(),
                                          "ocd-id": _hot_cache[entry]},
                                          upsert=True,
                                          safe=True)
    #print "Cache saved"
    _cache_touched = {}


def ocd_namer(obj):
    # ocd-person/UUID
    # ocd-organization/UUID
    if hasattr(obj, 'openstates_id'):
        ret = _hot_cache.get(obj.openstates_id)
        if ret is not None:
            return ret

    elif obj._type != 'membership':
        raise Exception  # We need stable IDs

    if obj._type == 'membership':
        return None

    return "ocd-{type_}/{uuid}".format(type_=obj._type, uuid=uuid.uuid1())


def is_ocd_id(string):
    return string.startswith("ocd-")


def save_objects(payload):
    for entry in payload:
        entry.validate()
        what = type_tables[type(entry)]
        table = getattr(nudb, what)

        _id = None
        try:
            _id = entry._id
        except AttributeError:
            pass

        ocd_id = ocd_namer(entry)
        if ocd_id:
            if _id and not is_ocd_id(_id):
                _id = None

            if _id is None:
                entry._id = ocd_id

        if what not in ["people", "memberships"]:
            jid = obj_to_jid(entry)
            entry.jurisdiction_id = jid


        eo = entry.as_dict()
        mongo_id = table.save(eo)

        if _id is None and ocd_id is None:
            entry._id = mongo_id

        if hasattr(entry, "openstates_id"):
            _hot_cache[entry.openstates_id] = entry._id
            _cache_touched[entry.openstates_id] = True

        if QUIET:
            sys.stdout.write(entry._type[0])
            sys.stdout.flush()


def save_object(payload):
    return save_objects([payload])


def migrate_legislatures(state):
    spec = {}
    if state:
        spec['_id'] = state

    for metad in db.metadata.find(spec):
        abbr = metad['abbreviation']
        geoid = "ocd-division/country:us/state:%s" % (abbr)

        cow = Organization(metad['legislature_name'],
                           classification="jurisdiction",
                           geography_id=geoid,
                           abbreviation=abbr)
        cow.openstates_id = abbr
        cow.add_source(metad['legislature_url'])

        for post in db.districts.find({"abbr": abbr}):

            cow.add_post(label="Member",
                         role="member",
                         num_seats=post['num_seats'],
                         chamber=post['chamber'],
                         district=post['name'])

        save_object(cow)
        meta = db.metadata.find_one({"_id": cow.openstates_id})
        if meta is None:
            raise Exception
        meta.pop("_id")
        meta['_id'] = cow.jurisdiction_id
        nudb.metadata.save(meta, safe=True)



def lookup_entry_id(collection, openstates_id):
    if openstates_id is None:
        return None

    hcid = _hot_cache.get(openstates_id, None)
    if hcid:
        return hcid

    org = getattr(nudb, collection).find_one({
        "openstates_id": openstates_id
    })

    if org is None:
        return None

    id_ = str(org['_id'])
    _hot_cache[openstates_id] = id_
    _cache_touched[openstates_id] = True
    return id_


def migrate_committees(state):

    def attach_members(committee, org):
        for member in committee['members']:
            osid = member.get('leg_id', None)
            person_id = lookup_entry_id('people', osid)
            if person_id:
                m = Membership(person_id, org._id)
                save_object(m)

    spec = {"subcommittee": None}

    if state:
        spec['state'] = state

    for committee in db.committees.find(spec):
        # OK, we need to do the root committees first, so that we have IDs that
        # we can latch onto down below.
        org = Organization(committee['committee'],
                           classification="committee")
        org.parent_id = lookup_entry_id('organizations', committee['state'])
        org.openstates_id = committee['_id']
        org.sources = committee['sources']
        # Look into posts; but we can't be sure.
        save_object(org)
        attach_members(committee, org)

    spec.update({"subcommittee": {"$ne": None}})

    for committee in db.committees.find(spec):
        org = Organization(committee['subcommittee'],
                           classification="committee")

        org.parent_id = lookup_entry_id(
            'organizations',
            committee['parent_id']
        ) or lookup_entry_id(
            'organizations',
            committee['state']
        )

        org.openstates_id = committee['_id']
        org.sources = committee['sources']
        # Look into posts; but we can't be sure.
        save_object(org)
        attach_members(committee, org)


def drop_existing_data(state):
    for entry in type_tables.values():
        print("Dropping %s" % (entry))
        nudb.drop_collection(entry)


def create_or_get_party(what):
    hcid = _hot_cache.get(what, None)
    if hcid:
        return hcid

    org = nudb.organizations.find_one({
        "name": what
    })
    if org:
        _hot_cache[what] = org['_id']
        _cache_touched[what] = True
        return org['_id']

    org = Organization(what, classification="party")
    org.openstates_id = what

    save_object(org)

    _hot_cache[what] = org._id
    _cache_touched[what] = True

    return org._id


def migrate_people(state):
    spec = {}
    if state:
        spec["state"] = state
    for entry in db.legislators.find(spec):
        who = Person(entry['full_name'])
        who.openstates_id = entry['_id']

        for k, v in {
            "photo_url": "image",
            "chamber": "chamber",
            "district": "district",
        }.items():
            if entry.get(k, None):
                setattr(who, v, entry[k])

        who.sources = entry['sources']

        home = entry.get('url', None)
        if home:
            who.add_link(home, "Homepage")

        blacklist = ["photo_url", "chamber", "district", "url",
                     "roles", "offices", "updated_at", "created_at",
                     "party", "state", "_locked_fields", "sources",
                     "active", "old_roles"]

        for key, value in entry.items():
            if key in blacklist or not value or key.startswith("_"):
                continue
            who.extras[key] = value

        legislature = lookup_entry_id('organizations', entry['state'])
        if legislature is None:
            raise Exception("Someone's in the void.")

        save_object(who)  # gives who an id, btw.

        party = entry.get('party', None)

        nudb.memberships.remove({"person_id": who._id}, safe=True)

        if party:
            m = Membership(who._id, create_or_get_party(entry['party']))
            save_object(m)

        m = Membership(who._id, legislature)

        chamber, district = (entry.get(x, None)
                             for x in ['chamber', 'district'])

        if chamber:
            m.chamber = chamber

        if district:
            m.district = district

        for office in entry.get('offices', []):
            note = office['name']
            for key, value in office.items():
                if not value or key in ["name", "type"]:
                    continue

                m.add_contact_detail(type=key, value=value, note=note)

        save_object(m)


def migrate_bills(state):
    #bills = db.bills.find({"actions.related_entities": {"$exists": True,
    #                                                    "$ne": []}})
    spec = {}
    if state:
        spec['state'] = state

    bills = db.bills.find(spec)
    for bill in bills:
        b = Bill(name=bill['bill_id'],
                 session=bill['session'],
                 title=bill['title'],
                 type=bill['type'])

        b.openstates_id = bill['_id']

        for source in bill['sources']:
            b.add_source(source['url'], note='old-source')

        for document in bill['documents']:
            b.add_document_link(name=document['name'], url=document['url'],
                                on_duplicate='ignore')  # Old docs are bad
            # about this

        for version in bill['versions']:
            kwargs = {}
            mime = version.get("mimetype", None)
            if mime:
                kwargs['mimetype'] = mime

            b.add_version_link(name=version['name'],
                               url=version['url'],
                               on_duplicate='ignore',  # Some old OS entries
                               # are not so good about this.
                               **kwargs)

        for subject in bill.get('subjects', []):
            b.add_subject(subject)

        for action in bill['actions']:
            related_entities = None
            related = action.get("related_entities")
            if related:
                related_entities = []
                for rentry in related:
                    type_ = {
                        "committee": "organizations",
                        "legislator": "people"
                    }[rentry['type']]

                    nid = rentry['id'] = lookup_entry_id(type_, rentry['id'])

                    rentry['_type'] = {
                        "committee": "organization",
                        "legislator": "person"
                    }[rentry.pop('type')]

                    related_entities.append(rentry)

            when = dt.datetime.strftime(action['date'], "%Y-%m-%d")

            translate = {"bill:introduced": "introduced",
                         "bill:reading:1": "reading:1",
                         "bill:reading:2": "reading:2",
                         "bill:reading:3": "reading:3"}

            type_ = [translate.get(x, None) for x in action['type']]

            b.add_action(description=action['action'],
                         actor=action['actor'],
                         date=when,
                         type=filter(lambda x: x is not None, type_),
                         related_entities=related_entities)

        for sponsor in bill['sponsors']:
            type_ = 'people'
            sponsor_id = sponsor.get('leg_id', None)

            if sponsor_id is None:
                type_ = 'organizations'
                sponsor_id = sponsor.get('committee_id', None)

            if sponsor_id:
                objid = lookup_entry_id(type_, sponsor_id)
                etype = {"people": "person",
                         "organizations": "organization"}[type_]

                kwargs = {}
                if objid is not None:
                    kwargs['entity_id'] = objid

                b.add_sponsor(
                    name=sponsor['name'],
                    sponsorship_type=sponsor['type'],
                    entity_type=etype,
                    primary=sponsor['type'] == 'primary',
                    chamber=sponsor.get('chamber', None),
                    **kwargs
                )

        b.validate()
        save_object(b)


def migrate_votes(state):
    spec = {}
    if state:
        spec['state'] = state

    for entry in db.votes.find(spec):
        #def __init__(self, session, date, type, passed,
        #             yes_count, no_count, other_count=0,
        #             chamber=None, **kwargs):

        when = dt.datetime.strftime(entry['date'], "%Y-%m-%d")
        if entry.get('type') is None:
            continue

        v = Vote(
            motion=entry['motion'],
            session=entry['session'],
            date=when,
            type=entry['type'],
            passed=entry['passed'],
            yes_count=entry['yes_count'],
            no_count=entry['no_count'],
            other_count=entry['other_count'],
            chamber=entry['chamber'])
        v.openstates_id = entry['_id']


        for source in entry['sources']:
            v.add_source(url=source['url'])

        if v.sources == []:
            continue  # emit warning

        for vtype in ['yes', 'no', 'other']:
            for voter in entry["%s_votes" % (vtype)]:
                id = voter.get('leg_id', None)
                hcid = _hot_cache.get(id, None)
                getattr(v, vtype)(name=voter['name'], id=hcid)

        hcid = _hot_cache.get(entry['bill_id'], None)
        bid = hcid
        v.add_bill(name=entry['bill_id'], id=bid)

        save_object(v)


def migrate_events(state):
    spec = {}
    if state:
        spec['state'] = state

    for entry in db.events.find(spec):

        e = Event(
            name=entry['description'],
            when=entry['when'],
            location=entry['location'],
            session=entry['session'],
        )
        e.openstates_id = entry['_id']

        if entry.get('end'):
            end = entry['end']
            try:
                end = dt.datetime.fromtimestamp(end)
            except ValueError:
                pass

            e.end = end

        for source in entry['sources']:
            e.add_source(url=source['url'])

        if e.sources == []:
            continue  # print warning

        for document in entry.get('documents', []):
            e.add_document(name=document.get('name'),
                           url=document['url'])

        agenda = None
        for bill in entry.get('related_bills', []):
            if agenda is None:
                agenda = e.add_agenda_item(
                    description="Bills up for Consideration"
                )

            hcid = _hot_cache.get(bill.get('id', None), None)
            bid = bill['bill_id']
            if bid is None:
                continue

            agenda.add_bill(bill=bid, id=hcid)

        for who in entry.get('participants', []):
            if who.get('participant_type') is None:
                continue

            hcid = _hot_cache.get(who.get('id', None), None)

            e.add_participant(
                name=who['participant'],
                type={
                    "committee": "organization",
                    "legislator": "person",
                    "person": "person",
                }[who['participant_type']],
                id=hcid,
                note=who['type'],
                chamber=who['chamber'])

        e.validate()
        save_object(e)


SEQUENCE = [
    load_hot_cache,
    #
    # XXX: WILL IGNORE STATE, DON'T ENABLE ME.
    #drop_existing_data,  # Not needed if we load the cache
    #
    migrate_legislatures,
    migrate_people,  # depends on legislatures
    #
    # XXX: migrate_people needs to be called for migrate_committees, for two
    #      reasons:
    #
    #   - committess look up person _id entries
    #   - migrating people drops memberships, which means it'd avoid
    #     dupes.
    #
    migrate_committees,  # depends on people
    migrate_bills,
    migrate_events,
    migrate_votes,
    write_hot_cache,
]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Re-convert a state.')
    parser.add_argument('state', type=str, help='State to rebuild',
                        default=None, nargs='?')

    parser.add_argument('--billy-server', type=str, help='Billy Mongo Server',
                        default="localhost")
    parser.add_argument('--billy-database', type=str,
                        help='Billy Mongo Database', default="fiftystates")
    parser.add_argument('--billy-port', type=int, help='Billy Mongo Server Port',
                        default=27017)


    parser.add_argument('--ocd-server', type=str, help='OCD Mongo Server',
                        default="localhost")
    parser.add_argument('--ocd-database', type=str, help='OCD Mongo Database',
                        default="larvae")
    parser.add_argument('--ocd-port', type=int, help='OCD Mongo Server Port',
                        default=27017)


    parser.add_argument('--quiet', action='store_false',
                        help='Dont spam my screen',
                        default=True)

    args = parser.parse_args()

    state = args.state
    QUIET = args.quiet

    connection = Connection(args.billy_server, args.billy_port)
    db = getattr(connection, args.billy_database)

    connection = Connection(args.ocd_server, args.ocd_port)
    nudb = getattr(connection, args.ocd_database)


    def handle_state(state):
        for seq in SEQUENCE:
            seq(state)

    if state:
        handle_state(state)
    else:
        for state in (x['abbreviation'] for x in db.metadata.find()):
            handle_state(state)

    print("")
    print("Migration complete.")
