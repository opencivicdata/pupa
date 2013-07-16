from .checkers import load_checkers
from pupa.utils import JSONEncoderPlus
from pymongo import Connection

from collections import defaultdict
import argparse
import json


report = defaultdict(list)

parser = argparse.ArgumentParser(description='Check an OCD Database.')
parser.add_argument('--server', type=str, help='OCD Mongo Server',
                    default="localhost")
parser.add_argument('--database', type=str, help='OCD Mongo Database',
                    default="ocd")
parser.add_argument('--port', type=int, help='OCD Mongo Server Port',
                    default=27017)

args = parser.parse_args()

connection = Connection(args.server, args.port)
db = getattr(connection, args.database)


for checker in load_checkers():
    for check in checker(db):
        report[check['collection']].append(check)


print json.dumps(report, indent=4, sort_keys=True, cls=JSONEncoderPlus)
