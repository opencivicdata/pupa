from django.db.models import Q
from opencivicdata.models import (Person, PersonIdentifier, PersonName, PersonContactDetail,
                                  PersonLink, PersonSource)
from .base import BaseImporter


class PersonImporter(BaseImporter):
    _type = 'person'
    model_class = Person
    related_models = {'identifiers': PersonIdentifier,
                      'other_names': PersonName,
                      'contact_details': PersonContactDetail,
                      'links': PersonLink,
                      'sources': PersonSource}

    def get_object(self, person):
        all_names = [person['name']] + [o['name'] for o in person['other_names']]
        return self.model_class.objects.get(
            Q(memberships__organization__jurisdiction_id=self.jurisdiction_id),
            (Q(name__in=all_names) | Q(other_names__name__in=all_names))
        )
