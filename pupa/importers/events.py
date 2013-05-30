from pupa.core import db
from .base import BaseImporter


class EventImporter(BaseImporter):
    _type = 'event'

    def get_db_spec(self, event):
        spec = {
            "description": event['description'],
            "start": event['start'],
            'jurisdiction_id': event['jurisdiction_id'],
        }
        return spec


    def prepare_object_from_json(self, obj):

        def person(what):
            spec = {}
            if 'chamber' in what:
                spec['chamber'] = what['chamber']
            spec['name'] = what['participant']
            # needs to get the right session
            return spec

        def bill(what):
            spec = {}
            if 'chamber' in what:
                spec['chamber'] = what['chamber']
            spec['name'] = what
            # needs to get the right session
            return spec

        def org(what):
            pass

        spec_generators = {
            "person": person,
            "bill": bill,
            "organization": org,
        }

        # XXX participants
        # XXX agenda

        for item in obj['agenda']:
            handler = spec_generators[who['entity_type']]
            spec = handler(who)
            spec['jurisdiction_id'] = obj['jurisdiction_id']

            rel_obj = db.events.find_one(spec)
            print rel_obj

        return obj
