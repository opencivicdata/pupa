from pupa.core import db


def match_membership(membership, other_entity):
    unmatched = membership.pop("unmatched_legislator")

    pid = membership.get('person_id')
    oid = membership.get('organization_id')

    if pid and oid:
        raise ValueError("Attempting to match an already matched membership")

    if not pid and not oid:
        raise ValueError("Attempting to match a hopeless membership "
                         "(no org id or person id)")


    def match_person(membership, person):
        if person['_type'] != 'person':
            raise ValueError("Matching a person, but not given a person.")

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

    if pid is None:
        return match_person(membership, other_entity)
    return match_org(membership, other_entity)


p = db.people.find_one({"_id": "ocd-person/b195d812-efe5-11e2-8334-f0def1bd7298"})
m = db.memberships.find_one({"_id": "ocd-membership/afec32ae-efe5-11e2-9936-f0def1bd7298"})


#print p, m
print match_membership(m, p)
