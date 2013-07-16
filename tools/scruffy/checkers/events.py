from .. import Check
from .common import common_checks, resolve
import datetime


def check(db):
    for event in db.events.find():
        for check in common_checks(event, 'event', 'events'):
            yield check

        location = event['location'].get('coordinates', None)
        if location:
            try:
                lat, lon = (float(location[x]) for x in (
                    'latitude', 'longitude'))
            except ValueError:
                for key in ['latitude', 'longitude']:
                    try:
                        float(location[key])
                    except ValueError:
                        yield Check(collection='events',
                                    id=event['_id'],
                                    tagname='%s-is-not-a-float' % (key),
                                    severity='critical')
            else:
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

        end = event.get('end')
        start = event.get('when')

        indt = lambda x: not isinstance(x, datetime.datetime)
        bad_datetime = False

        if end:
            if indt(end):
                bad_datetime = True
                yield Check(collection='events',
                            id=event['_id'],
                            tagname='end-is-not-datetime',
                            severity='important')

        if indt(start):
            bad_datetime = True
            yield Check(collection='events',
                        id=event['_id'],
                        tagname='start-is-not-datetime',
                        severity='important')


        if end and not bad_datetime:
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
