from .. import Check
from .common import common_checks


def check(db):
    for person in db.people.find():
        for check in common_checks(person, 'person', 'people'):
            yield check

        if db.memberships.find({"person_id": person['_id']}).count() == 0:
            yield Check(collection='people',
                        id=person['_id'],
                        tagname='person-with-no-memberships',
                        severity='important')
