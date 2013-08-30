from pupa.core import db


def collection_by_jurisdiction(jurisdiction_id, collection, field):
    """ Find all things in a jurisdiction """
    ids = getattr(db, collection).find({
        "jurisdiction_id": jurisdiction_id,
    }).distinct(field)
    if None in ids:
        ids.remove(None)
    return ids


def people_by_jurisdiction(jurisdiction_id):
    """ Find all people by a jurisdiction """
    return collection_by_jurisdiction(
        jurisdiction_id,
        'memberships',
        'person_id'
    )


def orgs_by_jurisdiction(jurisdiction_id):
    """ Find all orgs by a jurisdiction """
    return collection_by_jurisdiction(jurisdiction_id, 'organizations', '_id')


def bills_by_jurisdiction(jurisdiction_id):
    """ Find all bills by a jurisdiction """
    return collection_by_jurisdiction(jurisdiction_id, 'bills', '_id')


def people_by_name(name, people_ids=None, **kwargs):
    """ Find all people by their name. Optional people_ids _id constraint """
    spec = kwargs.copy()
    spec.update({"$or": [
        { "name": name },
        { "other_names.name": name },
        { "identifiers.identifier": name },
    ]})
    if people_ids is not None:
        # This isn't a raw if conditional, since you could pass
        # an empty list.
        spec["_id"] = {"$in": people_ids}
    return db.people.find(spec)


def bills_by_name(name, bill_ids=None, **kwargs):
    """ Find all bills by their name. Optional bill_ids _id constraint """
    spec = kwargs.copy()
    spec.update({"$or": [
        { "name": name },
        { "bill_id": name },
        { "alternate_titles.title": name },
        { "alternate_bill_ids.bill_id": name },
    ]})
    if bill_ids is not None:
        # This isn't a raw if conditional, since you could pass
        # an empty list.
        spec["_id"] = {"$in": bill_ids}
    return db.people.find(spec)


def orgs_by_name(name, org_ids=None, **kwargs):
    """ Find all orgs their name. Optional org_ids _id constraint """
    spec = kwargs.copy()

    spec.update({"$or": [
        { "name": name },
        { "other_names.name": name },
        { "identifiers.identifier": name },
    ]})

    if org_ids is not None:
        # This isn't a raw if conditional, since you could pass
        # an empty list.
        spec["_id"] = {"$in": org_ids}
    return db.organizations.find(spec)


def people_by_jurisdiction_and_name(jurisdiction_id, name, **kwargs):
    people_ids = people_by_jurisdiction(jurisdiction_id)
    people = people_by_name(name, people_ids=people_ids, **kwargs)
    return people


def orgs_by_jurisdiction_and_name(jurisdiction_id, name, **kwargs):
    org_ids = orgs_by_jurisdiction(jurisdiction_id)
    orgs = orgs_by_name(name, org_ids=org_ids, **kwargs)
    return orgs


def bills_by_jurisdiction_and_name(jurisdiction_id, name, **kwargs):
    bill_ids = bills_by_jurisdiction(jurisdiction_id)
    bills = bills_by_name(name, bill_ids=bill_ids, **kwargs)
    return bills
