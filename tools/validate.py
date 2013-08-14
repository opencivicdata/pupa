import pymongo
from larvae.organization import Organization
from larvae.person import Person
from larvae.event import Event

db = pymongo.Connection()['larvae']

def validate_collection(collection, Cls):
    count = 0
    good = 0
    for obj in db[collection].find():
        count += 1
        try:
            Cls.from_mongo(obj).validate()
            good += 1
        except Exception as e:
            print e
    print collection,good,'/',count,'validated'

validate_collection('organizations', Organization)
validate_collection('people', Person)
validate_collection('events', Event)
