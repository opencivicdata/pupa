from .. import Check
from .common import common_checks, resolve
import datetime


ERRORFUL_MEMBERSHIPS = []


def check(db):
    for membership in db.memberships.find({"person_id": None,
                                           "organization_id": None}):
        ERRORFUL_MEMBERSHIPS.append(membership['_id'])

        yield Check(collection='memberships',
                    id=membership['_id'],
                    tagname='membership-without-any-relation',
                    severity='critical',
                    data=membership)


    for membership in db.memberships.find({"person_id": None}):
        if membership['_id'] in ERRORFUL_MEMBERSHIPS:
            continue

        yield Check(collection='memberships',
                    id=membership['_id'],
                    tagname='membership-without-a-person',
                    severity='important',
                    data=membership)

    for membership in db.memberships.find({"organization_id": None}):
        if membership['_id'] in ERRORFUL_MEMBERSHIPS:
            continue

        yield Check(collection='memberships',
                    id=membership['_id'],
                    tagname='membership-without-an-organization',
                    severity='important',
                    data=membership)

    for membership in db.memberships.find({
        "unmatched_legislator.name": {"$ne": None},
        "person_id": {"$ne": None}}
    ):
        person = db.people.find_one({"_id": membership['person_id']})
        name = membership['unmatched_legislator']['name']
        if name not in person['other_names'] and name != person['name']:
            yield Check(collection='memberships',
                        id=membership['_id'],
                        tagname='membership-badly-linked',
                        severity='grave',
                        data=membership)

        yield Check(collection='memberships',
                    id=membership['_id'],
                    tagname='membership-linked-but-unlinked-data',
                    severity='important',
                    data=membership)
