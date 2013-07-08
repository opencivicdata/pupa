from .. import Check
from .common import common_checks, resolve


def check(db):
    for bill in db.bills.find():
        for check in common_checks(bill, 'bill', 'bills'):
            yield check

        for sponsor in bill['sponsors']:
            sid = sponsor.get("id")
            if sid:
                who = resolve(sponsor['_type'], sid)

                yield Check(collection='bills',
                            id=bill['_id'],
                            tagname='bad-sponsor-id',
                            severity='important',
                            data={"sponsor-id": sid, "name": sponsor['name']})
