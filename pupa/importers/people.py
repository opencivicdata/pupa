from collections import defaultdict
from django.db.models import Q
from opencivicdata.models import (Person, PersonIdentifier, PersonName, PersonContactDetail,
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
            # take into account other_names?
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
        spec['memberships__organization__jurisdiction_id'] = self.jurisdiction_id
        return spec

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
            # try and match based on birth_date
            if person['birth_date']:
                for m in matches:
                    if person['birth_date'] and m.birth_date == person['birth_date']:
                        return m

                # if we got here, no match based on birth_date, a new person?
                raise self.model_class.DoesNotExist('No Person: {} in {} with birth_date {}'
                                                    .format(all_names, self.jurisdiction_id,
                                                            person['birth_date']))
            raise SameNameError(person['name'])
