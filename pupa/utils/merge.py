from pupa.core import db


def match_membership(membership, other_entity):
    pid = membership.get('person_id')
    oid = membership.get('organization_id')

    if pid and oid:
        raise ValueError("Attempting to match an already matched membership")

    if not pid and not oid:
        raise ValueError("Attempting to match a hopeless membership "
                         "(no org id or person id)")

    unmatched = membership.pop("unmatched_legislator")

    l = lambda org, member: db.memberships.find_one({"person_id": member,
                                                     "organization_id": org})

    def match_person(membership, person):
        if person['_type'] != 'person':
            raise ValueError("Matching a person, but not given a person.")

        m = l(membership['organization_id'], person['_id'])
        if m:
            db.memberships.remove({"_id": membership['_id']})
            membership = m

        name = unmatched['name']
        if 'other_names' not in person:
            person['other_names'] = []

        if name not in person['other_names']:
            person['other_names'].append(name)

        membership['person_id'] = person['_id']
        db.memberships.save(membership)
        db.people.save(person)
        return (membership, person)

    def match_org(membership, org):
        if org['_type'] != 'organization':
            raise ValueError("Matching an organization, but not given an "
                             "organization.")
        membership['organization_id'] = org['_id']

        m = l(membership['organization_id'], membership['person_id'])
        if m:
            db.memberships.remove({"_id": membership['_id']})
            membership = m

        db.organizations.save(org)
        db.memberships.save(membership)
        return (membership, person)

    if pid is None:
        return match_person(membership, other_entity)
    return match_org(membership, other_entity)
