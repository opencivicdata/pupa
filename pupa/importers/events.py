import datetime
from pupa.core import db
from pupa.models import Event
from .base import BaseImporter


class EventImporter(BaseImporter):
    _type = 'event'
    _model_class = Event

    def get_db_spec(self, event):
        spec = {
            "description": event.description,
            "when": event.when,
            'jurisdiction_id': event.jurisdiction_id,
        }
        return spec

    def prepare_object_from_json(self, obj):

        def person(obj, what):
            spec = {}
            spec['session'] = obj['session']
            if 'chamber' in what:
                spec['chamber'] = what['chamber']
            spec['name'] = what['name']
            # needs to get the right session (current)
            return spec

        def bill(obj, what):
            spec = {}
            spec['session'] = obj['session']
            if 'chamber' in what:
                spec['chamber'] = what['chamber']
            spec['bill_id'] = what['name']
            # needs to get the right session (current)
            return spec

        def org(obj, what):
            spec = {}
            spec['session'] = obj['session']
            if 'chamber' in what:
                spec['chamber'] = what['chamber']
            spec['name'] = what['name']
            # needs to get the right session (current)
            return spec

        spec_generators = {
            "person": person,
            "bill": bill,
            "organization": org,
        }

        # XXX participants

        for item in obj['agenda']:
            for entity in item['related_entities']:
                handler = spec_generators[entity['type']]
                spec = handler(obj, entity)
                spec['jurisdiction_id'] = obj['jurisdiction_id']
                rel_obj = db.events.find_one(spec)
                if rel_obj:
                    entity['id'] = rel_obj['_id']
                else:
                    self.logger.warning('Unknown related entity: {name} '
                                        '({type})'.format(**entity))

        # update time
        obj['when'] = datetime.datetime.fromtimestamp(obj['when'])
        if obj.get('end'):
            obj['end'] = datetime.datetime.fromtimestamp(obj['end'])
        # TODO: handle timezones better

        return obj
