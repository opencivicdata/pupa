from .. import Check


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

    if obj['created_at'] > obj['updated_at']:
        yield Check(collection=plural,
                    id=obj['_id'],
                    tagname='updated-before-creation',
                    severity='critical')
