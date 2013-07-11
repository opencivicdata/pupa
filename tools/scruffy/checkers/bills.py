from .. import Check
from .common import common_checks, resolve


def check(db):
    for bill in db.bills.find():
        for check in common_checks(bill, 'bill', 'bills'):
            yield check

        for action in bill['actions']:
            for entity in action['related_entities']:
                wid = entity.get('id')
                if wid:
                    who = resolve(entity['_type'], wid)
                    if who is None:
                        yield Check(collection='bills',
                                    id=bill['_id'],
                                    tagname='bad-related-action-entity',
                                    severity='important',
                                    data={"id": wid,
                                          "name": entity['name']})

        for sponsor in bill['sponsors']:
            sid = sponsor.get("id")
            if sid:
                who = resolve(sponsor['_type'], sid)
                if who is None:
                    yield Check(collection='bills',
                                id=bill['_id'],
                                tagname='bad-sponsor-id',
                                severity='important',
                                data={"id": sid, "name": sponsor['name']})
