from pupa.core import db


def people_by_jurisdiction(jurisdiction_id):
    """ Find all people by a jurisdiction """
    people_ids = db.memberships.find({
        "jurisdiction_id": jurisdiction_id,
    }).distinct('person_id')

    if None in people_ids:
        people_ids.remove(None)
    return people_ids


def orgs_by_jurisdiction(jurisdiction_id):
    """ Find all orgs by a jurisdiction """
    org_ids = db.organizations.find({
        "jurisdiction_id": jurisdiction_id,
    }).distinct('_id')

    if None in org_ids:
        org_ids.remove(None)
    return org_ids


def people_by_name(name, people_ids=None):
    """ Find all people by their name. Optional people_ids _id constraint """
    spec = {"$or": [
        { "name": name },
        { "other_names.name": name }
    ]}
    if people_ids is not None:

        # This isn't a raw if conditional, since you could pass
        # an empty list.
        spec["_id"] = {"$in": people_ids}
    return db.people.find(spec)


def orgs_by_name(name, org_ids=None):
    """ Find all orgs their name. Optional org_ids _id constraint """

    spec = {"$or": [
        { "name": name },
        { "other_names.name": name },
        { "identifiers.identifier": name },
    ]}

    if org_ids is not None:
        # This isn't a raw if conditional, since you could pass
        # an empty list.
        spec["_id"] = {"$in": org_ids}
    return db.organizations.find(spec)


def people_by_jurisdiction_and_name(jurisdiction_id, name):
    people_ids = people_by_jurisdiction(jurisdiction_id)
    people = people_by_name(name, people_ids=people_ids)
    return people


def orgs_by_jurisdiction_and_name(jurisdiction_id, name):
    org_ids = orgs_by_jurisdiction(jurisdiction_id)
    orgs = orgs_by_name(name, org_ids=org_ids)
    return people
