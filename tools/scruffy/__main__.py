from . import db
from .checkers import load_checkers

from collections import defaultdict
import json


report = defaultdict(list)


for checker in load_checkers():
    for check in checker(db):
        report[check['collection']].append(check)


print json.dumps(report, indent=4, sort_keys=True)
