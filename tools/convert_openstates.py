#!/usr/bin/env python

from pupa.models import Organization, Membership, Person, Event, Vote, Bill

from collections import defaultdict
from pymongo import Connection
import datetime as dt
import operator
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
    if obj._openstates_id:
        jid = openstates_to_jid(obj._openstates_id)

    if jid is None:
        raise Exception("Can't auto-detect the Jurisdiction ID")

    return jid


def openstates_to_jid(osid):
    abbr = osid[:2]
    abbr = abbr.lower()
    jid = "ocd-jurisdiction/country:us/state:%s/legislature" % (abbr)
    return jid



def load_hot_cache(state):
    spec = {}
    if state:
        spec['state'] = state
    #print "Loading cache"
    for entry in nudb.openstates_cache.find(spec, timeout=False):
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
    if hasattr(obj, '_openstates_id'):
        ret = _hot_cache.get(obj._openstates_id)
        if ret is not None:
            return ret
        # OK. Let's try a last-ditch.
        what = type_tables[type(obj)]
        dbobj = getattr(nudb, what).find_one({
            "_openstates_id": obj._openstates_id
        })
        if dbobj:
            _hot_cache[dbobj['_openstates_id']] = dbobj['_id']
            return dbobj['_id']

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

        if what != 'people' and getattr(entry, '_openstates_id', None):
            jid = obj_to_jid(entry)
            entry.jurisdiction_id = jid

        entry.add_meta_software('openstates')
        eo = entry.as_dict()
        mongo_id = table.save(eo)

        if _id is None and ocd_id is None:
            entry._id = mongo_id

        if hasattr(entry, "_openstates_id"):
            _hot_cache[entry._openstates_id] = entry._id
            _cache_touched[entry._openstates_id] = True

        if QUIET:
            sys.stdout.write(entry._type[0])
            sys.stdout.flush()


def save_object(payload):
    return save_objects([payload])


def migrate_legislatures(state):
    spec = {}
    if state:
        spec['_id'] = state

    for metad in db.metadata.find(spec, timeout=False):
        abbr = metad['abbreviation']
        geoid = "ocd-division/country:us/state:%s" % (abbr)
        for chamber in metad['chambers']:
            cn = metad['chambers'][chamber]['name']
            cow = Organization("%s, %s" % (metad['legislature_name'], cn),
                               classification="legislature",
                               chamber=chamber,
                               division_id=geoid,
                               abbreviation=abbr)
            cow._openstates_id = "%s-%s" % (abbr, chamber)
            cow.add_source(metad['legislature_url'])

            for post in db.districts.find({"abbr": abbr}):
                if post['chamber'] != chamber:
                    continue

                cow.add_post(label="Member",
                             role="member",
                             num_seats=post['num_seats'],
                             id=post['name'])

            save_object(cow)

        meta = db.metadata.find_one({"_id": cow.abbreviation})
        if meta is None:
            raise Exception
        meta.pop("_id")
        meta['_id'] = cow.jurisdiction_id

        for badtag in ["latest_json_url", "latest_json_date",
                       "latest_csv_url", "latest_csv_date",]:
            meta.pop(badtag)

        nudb.jurisdictions.save(meta)



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


def get_current_term(jid):
    meta = nudb.jurisdictions.find_one({"_id": jid})
    term = meta['terms'][-1]
    return term


def migrate_committees(state):

    def attach_members(committee, org):
        term = get_current_term(obj_to_jid(org))
        for member in committee['members']:
            osid = member.get('leg_id', None)
            person_id = lookup_entry_id('people', osid)
            if person_id:
                m = Membership(person_id, org._id,
                               role=member['role'],
                               chamber=org.chamber,
                               # term=term['name'],
                               start_date=str(term['start_year']))
                m.add_extra('term', term['name'])
                # We can assume there's no end_year because it's a current
                # member of the committee. If they left the committee, we don't
                # know about it yet :)
                save_object(m)

                if m.role != 'member':
                    # In addition to being the (chair|vice-chair),
                    # they should also be noted as a member.
                    m = Membership(person_id, org._id,
                                   role='member',
                                   chamber=org.chamber,
                                   start_date=str(term['start_year']))
                    m.add_extra('term', term['name'])
                    save_object(m)

    spec = {"subcommittee": None}

    if state:
        spec['state'] = state

    for committee in db.committees.find(spec, timeout=False):
        # OK, we need to do the root committees first, so that we have IDs that
        # we can latch onto down below.
        org = Organization(committee['committee'],
                           classification="committee")
        org.chamber = committee['chamber']
        org.parent_id = lookup_entry_id('organizations', committee['state'])
        org.identifiers = [{'scheme': 'openstates',
                            'identifier': committee['_id']}]
        org._openstates_id = committee['_id']
        org.sources = committee['sources']
        org.created_at = committee['created_at']
        org.updated_at = committee['updated_at']
        # Look into posts; but we can't be sure.
        save_object(org)
        attach_members(committee, org)

    spec.update({"subcommittee": {"$ne": None}})

    for committee in db.committees.find(spec, timeout=False):
        org = Organization(committee['subcommittee'],
                           classification="committee")

        org.parent_id = lookup_entry_id(
            'organizations',
            committee['parent_id']
        ) or lookup_entry_id(
            'organizations',
            committee['state']
        )

        org.identifiers = [{'scheme': 'openstates',
                           'identifier': committee['_id']}]
        org._openstates_id = committee['_id']
        org.sources = committee['sources']
        org.chamber = committee['chamber']
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

    save_object(org)

    _hot_cache[what] = org._id
    _cache_touched[what] = True

    return org._id


def migrate_people(state):
    spec = {}
    if state:
        spec["state"] = state
    for entry in db.legislators.find(spec, timeout=False):
        jurisdiction_id = openstates_to_jid(entry['_id'])

        who = Person(entry['full_name'])
        who.identifiers = [{'scheme': 'openstates',
                           'identifier': entry['_id']}]
        who._openstates_id = entry['_id']
        who.created_at = entry['created_at']
        who.updated_at = entry['updated_at']
        if who.name != entry['_scraped_name']:
            who.add_name(entry['_scraped_name'])

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

        vsid = entry.get('votesmart_id')
        if vsid:
            who.add_identifier(vsid, 'votesmart-id')

        tdid = entry.get('transparencydata_id')
        if tdid:
            who.add_identifier(tdid, 'transparencydata-id')

        blacklist = ["photo_url", "chamber", "district", "url",
                     "roles", "offices", "party", "state", "sources",
                     "active", "old_roles", "_locked_fields", "created_at",
                     "updated_at", "transparencydata_id", "votesmart_id",
                     "leg_id", "email", "phone", "fax", "_scraped_name",
                     "_id", "_all_ids", "full_name", "country", "level",
                     "office_address", "suffixes", "_type"]
        # The above is a list of keys we move over by hand later.

        for key, value in entry.items():
            if key in blacklist or not value:  # or key.startswith("_"):
                continue
            who.extras[key] = value

        who.add_meta('locked_fields', entry.get('_locked_fields', []))

        chamber = entry.get('chamber')
        if chamber == "joint":
            continue

        legislature = None
        if chamber:
            legislature = lookup_entry_id('organizations', "%s-%s" % (
                entry['state'],
                chamber,
            ))

            if legislature is None:
                print chamber, entry['state'], entry['_id']
                raise Exception("Someone's in the void.")

        save_object(who)  # gives who an id, btw.

        party = entry.get('party', None)
        nudb.memberships.remove({"person_id": who._id}, safe=True)

        if party:
            m = Membership(who._id, create_or_get_party(entry['party']))
            save_object(m)

        if legislature:
            term = get_current_term(jurisdiction_id)
            m = Membership(who._id, legislature,
                           chamber=chamber,
                           start_date=str(term['start_year']))
            m.add_extra('term', term['name'])

            chamber, district = (entry.get(x, None)
                                 for x in ['chamber', 'district'])

            if chamber:
                m.chamber = chamber

            if district:
                m.post_id = district

            for key in ['email', 'fax', 'phone']:
                if key in entry and entry[key]:
                    m.add_contact_detail(type=key,
                                         value=entry[key],
                                         note=key)

            if entry.get("office_address"):
                m.add_contact_detail(type='office',
                                     value=entry['office_address'],
                                     note='Office Address')

            for office in entry.get('offices', []):
                note = office['name']
                for key, value in office.items():
                    if not value or key in ["name", "type"]:
                        continue
                    m.add_contact_detail(type=key, value=value, note=note)

            save_object(m)

        for session in entry.get('old_roles', []):
            roles = entry['old_roles'][session]
            meta = nudb.jurisdictions.find_one({"_id": obj_to_jid(who)})
            term = None

            for role in roles:
                term = role['term']
                t = None
                for to in meta['terms']:
                    if term == to['name']:
                        term = to
                        break
                else:
                    raise Exception("No term found?")

                start_year = term['start_year']
                end_year = term['end_year']

                if 'committee' in role:
                    cid = role.get('committee_id')
                    if cid:
                        jid = _hot_cache.get(cid)
                        if jid:
                            m = Membership(who._id, jid,
                                           role='member',
                                           start_date=str(start_year),
                                           end_date=str(end_year),
                                           chamber=role['chamber'])
                            m.add_extra('term', term['name'])

                            if "position" in role:
                                m.role = role['position']

                            save_object(m)

                            if m.role != 'member':
                                # In addition to being the (chair|vice-chair),
                                # they should also be noted as a member.
                                m = Membership(who._id,
                                               jid,
                                               role='member',
                                               start_date=str(start_year),
                                               end_date=str(end_year),
                                               chamber=role['chamber'])
                                m.add_extra('term', term['name'])
                                save_object(m)

                if 'district' in role:
                    oid = "{state}-{chamber}".format(**role)
                    leg = nudb.organizations.find_one({"_openstates_id": oid})
                    if leg:
                        m = Membership(who._id, leg['_id'],
                                       start_date=str(start_year),
                                       end_date=str(end_year),
                                       post_id=role['district'],
                                       chamber=role['chamber'])
                        m.add_extra('term', term['name'])
                        save_object(m)


def migrate_bills(state):
    spec = {}
    if state:
        spec['state'] = state

    bills = db.bills.find(spec, timeout=False)
    for bill in bills:

        ocdid = _hot_cache.get('{state}-{chamber}'.format(**bill))
        org = nudb.organizations.find_one({"_id": ocdid})
        org_name = org['name']
        if not org or not org_name or not ocdid:
            raise Exception("""Can't look up chamber this legislative
                            instrument was introduced into.""")

        b = Bill(name=bill['bill_id'],
                 organization=org_name,
                 organization_id=ocdid,
                 session=bill['session'],
                 title=bill['title'],
                 chamber=bill['chamber'],
                 type=bill['type'],
                 created_at=bill['created_at'],
                 updated_at=bill['updated_at'])

        b.identifiers = [{'scheme': 'openstates',
                         'identifier': bill['_id']}]
        b._openstates_id = bill['_id']

        blacklist = ["bill_id", "session", "title", "chamber", "type",
                     "created_at", "updated_at", "sponsors", "actions",
                     "versions", "sources", "state", "action_dates",
                     "documents", "level", "country", "alternate_titles",
                     "subjects", "_id", "type", "_type", "_term", "_all_ids",
                     "summary", "_current_term", "_current_session"]

        for key, value in bill.items():
            if key in blacklist or not value:  # or key.startswith("_"):
                continue
            b.extras[key] = value

        for subject in bill.get('subjects', []):
            b.add_subject(subject)

        if 'summary' in bill and bill['summary']:
            # OpenStates only has one at most. let's just convert it
            # blind.
            b.add_summary('summary', bill['summary'])

        if 'alternate_titles' in bill:
            b.other_titles = [{"title": x, "note": None}
                              for x in bill['alternate_titles']]

        for source in bill['sources']:
            b.add_source(source['url'], note='OpenStates source')

        for document in bill['documents']:
            b.add_document_link(
                mimetype=document.get('mimetype'),
                name=document['name'],
                url=document['url'],
                document_id=document['doc_id'],
                on_duplicate='ignore')  # Old docs are bad about this

        b.add_extra('action_dates', bill['action_dates'])

        for version in bill['versions']:
            kwargs = {}
            mime = version.get("mimetype", version.get("+mimetype"))
            if mime:
                kwargs['mimetype'] = mime

            b.add_version_link(name=version['name'],
                               url=version['url'],
                               on_duplicate='ignore',
                               document_id=version['doc_id'],
                               # ^^^ Some old OS entries are not so
                               # good about this.
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
                    if nid:
                        if "ocd" not in nid:
                            raise Exception("Non-OCD id")

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

            kwargs = {}
            if sponsor_id:
                objid = lookup_entry_id(type_, sponsor_id)

                if objid is not None:
                    kwargs['entity_id'] = objid

            etype = {"people": "person",
                     "organizations": "organization"}[type_]

            #if sponsor.get('official_type'):
            #    kwargs['official_type'] = sponsor['official_type']
            # Not needed???

            b.add_sponsor(
                name=sponsor['name'],
                sponsorship_type=sponsor['type'],
                entity_type=etype,
                primary=sponsor['type'] == 'primary',
                chamber=sponsor.get('chamber', None),
                **kwargs)

        b.validate()
        save_object(b)


def migrate_votes(state):
    spec = {}
    if state:
        spec['state'] = state

    for entry in db.votes.find(spec, timeout=False):
        #def __init__(self, session, date, type, passed,
        #             yes_count, no_count, other_count=0,
        #             chamber=None, **kwargs):

        when = dt.datetime.strftime(entry['date'], "%Y-%m-%d")
        if entry.get('type') is None:
            continue

        org_name = entry.get('committee')
        if org_name:
            # There's a committee tied to this vote.
            org_id = entry.get('committee_id')
            ocdid = _hot_cache.get(org_id)
        else:
            # OK. We don't have a committee. We should have a chamber.
            # Let's fallback on the COW.
            ocdid = _hot_cache.get('{state}-{chamber}'.format(**entry))
            org = nudb.organizations.find_one({"_id": ocdid})
            if ocdid is None or org is None:
                if entry['chamber'] == 'joint':
                    print ""
                    print ""
                    print "XXX: Vote is marked as joint, but has no committee."
                    print "     This is likely (totally is) a bug. Please"
                    print "     fix the scraper. We'll pass on it in the"
                    print "     meantime."
                    print ""
                    print "     VoteID: %s" % (entry['_id'])
                    print ""
                    continue

                raise Exception("""Can't look up the legislature? Something
                                 went wrong internally. The cache might be
                                 wrong for some reason. Look into this.""")
            org_name = org['name']

        v = Vote(
            organization=org_name,
            organization_id=ocdid,
            motion=entry['motion'],
            session=entry['session'],
            date=when,
            type=entry['type'],
            passed=entry['passed'],
            yes_count=entry['yes_count'],
            no_count=entry['no_count'],
            other_count=entry['other_count'],
            chamber=entry['chamber'],
            #created_at=entry['created_at'],
            #updated_at=entry['updated_at'],
        )
        v.identifiers = [{'scheme': 'openstates',
                         'identifier': entry['_id']}]
        v._openstates_id = entry['_id']


        for source in entry['sources']:
            v.add_source(**source)

        if v.sources == []:
            continue  # emit warning

        for vtype in ['yes', 'no', 'other']:
            for voter in entry["%s_votes" % (vtype)]:
                id = voter.get('leg_id', None)
                hcid = _hot_cache.get(id, None)
                getattr(v, vtype)(name=voter['name'], id=hcid)

        hcid = _hot_cache.get(entry['bill_id'], None)
        bid = hcid

        # The bill_id coming off the entry is an ugly OpenStates bigID.
        # We need to actually get the bill and use that for this. This
        # results in kinda a silly slowdown. Perhaps we can cache titles.

        bill_id = entry['bill_id']  # as fallback.
        if bid:
            dbill = nudb.bills.find_one({"_id": bid})
            if dbill:
                bill_id = dbill['name']

        v.set_bill(what=bill_id, id=bid, chamber=entry['chamber'])

        save_object(v)


def migrate_events(state):
    spec = {}
    if state:
        spec['state'] = state

    for entry in db.events.find(spec, timeout=False):

        e = Event(
            name=entry['description'],
            when=entry['when'],
            location=entry['location'],
            session=entry['session'],
            updated_at=entry['updated_at'],
            created_at=entry['created_at'],
            type=entry['type'],
        )
        e.identifiers = [{'scheme': 'openstates',
                         'identifier': entry['_id']}]
        e._openstates_id = entry['_id']
        if entry.get('+location_url'):
            e.add_location_url(entry['+location_url'])

        link = entry.get('link', entry.get("+link"))
        if link:
            e.add_link(link, 'link')

        blacklist = ["description", "when", "location", "session",
                     "updated_at", "created_at", "end", "sources",
                     "documents", "related_bills", "state", "+link",
                     "link", "level", "participants", "country",
                     "_all_ids", "type",]

        e.status = entry.get('status')
        typos = {
            "canceled": "cancelled"
        }
        if e.status in typos:
            e.status = typos[e.status]

        for key, value in entry.items():
            if key in blacklist or not value or key.startswith("_"):
                continue
            e.extras[key] = value

        if entry.get('end'):
            end = entry['end']
            try:
                end = dt.datetime.fromtimestamp(end)
            except TypeError:
                pass

            e.end = end

        for source in entry['sources']:
            e.add_source(url=source['url'])

        if e.sources == []:
            continue  # print warning

        for document in entry.get('documents', []):
            e.add_document(name=document.get('name'),
                           document_id=document.get('doc_id'),
                           url=document['url'],
                           mimetype=document.get(
                               "mimetype", document.get(
                                   "+mimetype",
                                   "application/octet-stream")))
            # Try to add the mimetype. If it fails, fall back to a generic
            # undeclared application/octet-stream.

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
            participant_type = who.get('participant_type', 'committee')
            # I've gone through the backlog of OpenStates data, they are
            # all committees of some sort.

            who_chamber = who.get('chamber')
            if who_chamber is None:
                for chamber in ["_chamber", "+chamber"]:
                    f = who.get(chamber)
                    if f:
                        who_chamber = f
                        break

            if who_chamber is None:
                # Freak of nature ...
                continue

            hcid = _hot_cache.get(who.get('id', None), None)

            e.add_participant(
                name=who['participant'],
                type={
                    "committee": "organization",
                    "legislator": "person",
                    "person": "person",
                }[participant_type],
                id=hcid,
                note=who['type'],
                chamber=who_chamber)

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
                        default="opencivicdata")
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
        print "now processing ", state
        for seq in SEQUENCE:
            seq(state)

    if state:
        handle_state(state)
    else:
        for state in (x['abbreviation'] for x in
                      db.metadata.find(timeout=False)):
            handle_state(state)

    print("")
    print("Migration complete.")
