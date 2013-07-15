from .. import Check
from ..core import db
import re

atz = "[A-Fa-f0-9]"
ocd_id_re = "ocd-(\w+)/%s{8}-%s{4}-%s{4}-%s{4}-%s{12}" % (
    atz, atz, atz, atz, atz
)
ocd_id = re.compile(ocd_id_re)


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

    if obj['_id'] is None:
        yield Check(collection=plural,
                    id=obj['_id'],
                    tagname='%s-has-null-_id' % (singular),
                    severity='critical')

    elif singular not in ['membership']:
        id_ = str(obj['_id'])  # If we catch an ObjectId
        if not ocd_id.match(id_):
            yield Check(collection=plural,
                        id=obj['_id'],
                        tagname='%s-has-bad-_id' % (singular),
                        severity='critical')

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
