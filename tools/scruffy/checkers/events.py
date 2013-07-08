from .. import Check
from .common import common_checks


def check(db):
    for event in db.events.find():
        for check in common_checks(event, 'event', 'events'):
            yield check
