from django.db.models import Q
from opencivicdata.models import (Person, PersonIdentifier, PersonName, PersonContactDetail,
                                  PersonLink, PersonSource)
from .base import BaseImporter


class PersonImporter(BaseImporter):
    _type = 'person'
    model_class = Person
    related_models = {'identifiers': {},
                      'other_names': {},
                      'contact_details': {},
                      'links': {},
                      'sources': {}}

    def get_object(self, person):
        all_names = [person['name']] + [o['name'] for o in person['other_names']]
        return self.model_class.objects.get(
            Q(memberships__organization__jurisdiction_id=self.jurisdiction_id),
            (Q(name__in=all_names) | Q(other_names__name__in=all_names))
        )
