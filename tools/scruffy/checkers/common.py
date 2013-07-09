from .. import Check
from ..core import db


def common_checks(obj, singular, plural):
    if obj['_type'] != singular:
        yield Check(collection=plural,
                    id=obj['_id'],
                    tagname='%s-has-invalid-_type' % (singular),
                    severity='critical')

    if obj.get('sources', []) == []:
        yield Check(collection=singular,
                    id=obj['_id'],
                    tagname='%s-has-no-sources' % (singular),
                    severity='critical')

    if all([x in obj for x in ['created_at', 'updated_at']]):
        if obj['created_at'] > obj['updated_at']:
            yield Check(collection=plural,
                        id=obj['_id'],
                        tagname='updated-before-creation',
                        severity='critical')


def resolve(type_, id_):
    collection = {
        "person": db.people,
        "organization": db.orgnizations,
        "bill": db.bills,
    }[type_]

    return collection.find_one({"_id": id_})
