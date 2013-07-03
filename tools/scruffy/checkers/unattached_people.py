from .. import Check


def check(db):
    for person in db.people.find():
        if db.memberships.find({"person_id": person['_id']}).count() == 0:
            yield Check(collection='people',
                        id=person['_id'],
                        tagname='person-with-no-memberships',
                        severity='important')
