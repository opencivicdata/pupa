from .. import Check
from ..core import db


def common_checks(obj, singular, plural):

    if obj.get('jurisdiction_id'):
        org = db.metadata.find_one({
            "_id": obj['jurisdiction_id']
        })
        if org is None:
            yield Check(collection=plural,
                        id=obj['_id'],
                        tagname='%s-has-unlinked-jurisdiction-id' % (singular),
                        severity='important')

    if obj.get("_type") is None:
        yield Check(collection=plural,
                    id=obj['_id'],
                    tagname='%s-is-missing-_type' % (singular),
                    severity='critical')

    elif obj['_type'] != singular:
        yield Check(collection=plural,
                    id=obj['_id'],
                    tagname='%s-has-invalid-_type' % (singular),
                    severity='critical')

    if obj.get('sources', []) == []:
        if not obj.get('classification', None) in ['party']:
            yield Check(collection=plural,
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
        "organization": db.organizations,
        "bill": db.bills,
    }[type_]

    return collection.find_one({"_id": id_})
