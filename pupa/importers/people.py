from collections import defaultdict, Counter
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
        by_source = defaultdict(list)
        for _, person in dicts:
            if person['source_identified']:
                for source in person['sources']:
                    by_source[source['url']].append(person['name'])
            # take into account other_names?
            by_name[person['name']].append(person)
            for other in person['other_names']:
                by_name[other['name']].append(person)

        # check for duplicates
        for name, people in by_name.items():
            if len(people) > 1:
                for person in people:
                    if person['birth_date'] == '' and not person['source_identified']:
                        raise SameNameError(name)
        for source, namelist in by_source.items():
            namecounts = Counter(namelist)
            for n, count in namecounts.items():
                if count > 1:
                    raise Exception('{} has duplicate names'.format(source))

        return dicts

    def limit_spec(self, spec):
        return spec

    def get_object(self, person):
        if person['source_identified']:
            # special lookup for when we're assuming that, for every combination
            # of:
            #
            #    person.name
            #    person.source.url
            #    (optional) person.source.note
            #
            # it is assumed that there is a unique person in the world that is
            # identified. This is particularly useful for non-governmental
            # people.

            try:
                person_sources = person['sources']
            except KeyError:
                raise KeyError('source-identified person {} has no sources!'.format(
                    person['name']))

            matches = []

            for source in person_sources:
                spec = {'name': person['name'],
                        'sources__url': source['url']}

                if source['note']:
                    spec['sources__note'] = source['note']

                source_matches = self.model_class.objects.filter(**spec)

                if len(source_matches) > 1:
                    raise Exception(
                        'person {} at source {} with note {} has multiple matches'.format(
                            person['name'], source['url'], source['note']))
                elif len(source_matches) == 1:
                    matches.append(source_matches[0])
                else:
                    continue

            if len(matches) == 0:
                raise self.model_class.DoesNotExist(
                    'No Person: {} with any of source urls {}'.format(
                        person['name'], [s['url'] for s in person_sources]))
            elif len(matches) == 1:
                return matches[0]
        else:
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
