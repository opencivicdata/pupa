from .. import Check
from .common import common_checks, resolve


def check(db):
    for event in db.events.find():
        for check in common_checks(event, 'event', 'events'):
            yield check

        for agenda in event['agenda']:
            for entity in agenda['related_entities']:
                if entity['id']:
                    wid = resolve(entity['type'], entity['id'])
                    if wid is None:
                        yield Check(collection='events',
                                    id=event['_id'],
                                    tagname='bad-related-entity',
                                    severity='important',
                                    data={"id": wid,
                                          "name": entity['name']})
