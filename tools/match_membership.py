#!/usr/bin/env python

from pupa.core import db
from pupa.utils.merge import match_membership
import argparse
import sys


parser = argparse.ArgumentParser(description='Match a person.')

parser.add_argument(
    'membership',
    type=str,
    help='Membership to Match',
)

parser.add_argument(
    'related',
    type=str,
    help='Related Entity',
)

args = parser.parse_args()


table = {
    "ocd-person": db.people,
    "ocd-organization": db.organizations
}[args.related.split("/", 1)[0]]


membership = db.memberships.find_one({"_id": args.membership})
if membership is None:
    print "Invalid Membership"
    sys.exit(1)

entity = table.find_one({"_id": args.related})
if entity is None:
    print "Invalid Entity"
    sys.exit(1)

try:
    membership, entity = match_membership(membership, entity)
except ValueError as e:
    print "Error: %s" % (e)
    sys.exit(2)
