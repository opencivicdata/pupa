from collections import defaultdict
from django.db.models import Q
from opencivicdata.core.models import (Person, PersonIdentifier, PersonName, PersonContactDetail,
                                       PersonLink, PersonSource)
from .base import BaseImporter
from ..exceptions import SameNameError


class PersonImporter(BaseImporter):
    _type = 'person'
    model_class = Person
    related_models = {'identifiers': (PersonIdentifier, 'person_id', {}),
                      'other_names': (PersonName, 'person_id', {}),
                      'contact_details': (PersonContactDetail, 'person_id', {}),
                      'links': (PersonLink, 'person_id', {}),
                      'sources': (PersonSource, 'person_id', {}),
                      }

    def _prepare_imports(self, dicts):
        dicts = list(super(PersonImporter, self)._prepare_imports(dicts))

        by_name = defaultdict(list)
        for _, person in dicts:
            by_name[person['name']].append(person)
            for other in person['other_names']:
                by_name[other['name']].append(person)

        # check for duplicates
        for name, people in by_name.items():
            if len(people) > 1:
                for person in people:
                    if person['birth_date'] == '':
                        raise SameNameError(name)

        return dicts

    def limit_spec(self, spec):
        """
        Whenever we do a Pseudo ID lookup from the database, we need to limit
        based on the memberships -> organization -> jurisdiction, so we scope
        the resolution.
        """
        if list(spec.keys()) == ['name']:
            # if we're just resolving on name, include other names and family name
            name = spec['name']
            return ((Q(name=name) | Q(other_names__name=name) | Q(family_name=name)) &
                    Q(memberships__organization__jurisdiction_id=self.jurisdiction_id))
        spec['memberships__organization__jurisdiction_id'] = self.jurisdiction_id
        return spec

    def get_object(self, person):
        all_names = [person['name']] + [o['name'] for o in person['other_names']]

        matches = list(self.model_class.objects.filter(
            Q(memberships__organization__jurisdiction_id=self.jurisdiction_id),
            (Q(name__in=all_names) | Q(other_names__name__in=all_names))
        ).distinct('id'))

        matches_length = len(matches)
        if matches_length == 1 and not matches[0].birth_date:
            return matches[0]
        elif matches_length == 0:
            raise self.model_class.DoesNotExist(
                'No Person: {} in {}'.format(all_names, self.jurisdiction_id))
        else:
            # Try and match based on birth_date.
            if person['birth_date']:
                for match in matches:
                    if person['birth_date'] and match.birth_date == person['birth_date']:
                        return match

                # If we got here, no match based on birth_date, a new person?
                raise self.model_class.DoesNotExist(
                    'No Person: {} in {} with birth_date {}'.format(
                        all_names, self.jurisdiction_id, person['birth_date']))

            raise SameNameError(person['name'])
