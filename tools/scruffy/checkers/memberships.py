from .. import Check
from .common import common_checks, resolve
import datetime


def check(db):
    for membership in db.memberships.find({"person_id": None}):
        yield Check(collection='memberships',
                    id=membership['_id'],
                    tagname='membership-without-a-person',
                    severity='critical',
                    data=membership)

    for membership in db.memberships.find({"organization_id": None}):
        yield Check(collection='memberships',
                    id=membership['_id'],
                    tagname='membership-without-an-organization',
                    severity='critical',
                    data=membership)
