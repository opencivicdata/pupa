from .. import Check
from .common import common_checks, resolve


def check(db):
    for event in db.events.find():
        for check in common_checks(event, 'event', 'events'):
            yield check

        location = event['location'].get('coordinates', None)
        if location:
            lat, lon = (float(location[x]) for x in ('latitude', 'longitude'))
            if abs(lat) > 90:
                yield Check(collection='events',
                            id=event['_id'],
                            tagname='latitude-is-out-of-range',
                            severity='critical')

            if abs(lon) > 180:
                yield Check(collection='events',
                            id=event['_id'],
                            tagname='longitude-is-out-of-range',
                            severity='critical')

        if event.get('end'):
            if event.get('when') > event.get('end'):
                yield Check(collection='events',
                            id=event['_id'],
                            tagname='ends-before-it-starts',
                            severity='important')


        for agenda in event['agenda']:
            for entity in agenda['related_entities']:
                if entity['id']:
                    wid = resolve(entity['type'], entity['id'])
                    if wid is None:
                        yield Check(collection='events',
                                    id=event['_id'],
                                    tagname='bad-related-entity',
                                    severity='important',
                                    data=entity)
