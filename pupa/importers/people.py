from django.db.models import Q
from opencivicdata.models import Person
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
        matches = list(self.model_class.objects.filter(
            Q(memberships__organization__jurisdiction_id=self.jurisdiction_id),
            (Q(name__in=all_names) | Q(other_names__name__in=all_names))
        ).distinct('id'))
        if len(matches) == 1:
            return matches[0]
        elif len(matches) == 0:
            raise self.model_class.DoesNotExist('No Person: {} in {}'.format(all_names,
                                                                             self.jurisdiction_id))
        else:
            raise self.model_class.MultipleObjectsReturned('Multiple People: {} in {}'.format(
                all_names, self.jurisdiction_id))
