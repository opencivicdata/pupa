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
            spec['name'] = what['entity']
            # needs to get the right session (current)
            return spec

        def bill(what):
            spec = {}
            if 'chamber' in what:
                spec['chamber'] = what['chamber']
            spec['name'] = what['entity']
            # needs to get the right session (current)
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
            for entity in item['related_entities']:
                handler = spec_generators[entity['entity_type']]
                spec = handler(entity)
                spec['jurisdiction_id'] = obj['jurisdiction_id']
                rel_obj = db.events.find_one(spec)
                if rel_obj:
                    entity['entity_id'] = rel_obj['_id']
                else:
                    self.logger.warning('Unknown related entity: {entity} '
                                        '({entity_type})'.format(**entity))
        return obj
