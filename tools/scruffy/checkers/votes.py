from .. import Check
from .common import common_checks
from collections import defaultdict


def check(db):
    for vote in db.votes.find():
        for check in common_checks(vote, 'vote', 'votes'):
            yield check

        org = db.metadata.find_one({
            "_id": vote['jurisdiction_id']
        })
        if org is None:
            yield Check(collection='votes',
                        id=vote['_id'],
                        tagname='vote-has-invalid-jurisdiction-id',
                        severity='important')

        count = defaultdict(lambda: 0)
        for v in vote['roll_call']:
            count[v['vote_type']] += 1

        for t, c in ((x['vote_type'], x['count'])
                     for x in vote['vote_counts']):

            if count[t] != c:
                yield Check(collection='votes',
                            id=vote['_id'],
                            tagname='vote-has-bad-count',
                            severity='normal',
                            data={"vote_type": t,
                                  "off_by": abs(c - count[t]),
                                  "counted": count[t],
                                  "scraped": c})
