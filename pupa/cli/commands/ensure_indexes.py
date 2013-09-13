from __future__ import print_function
import itertools
from pupa.core import db
from .base import BaseCommand
from pymongo import ASCENDING, DESCENDING


class Command(BaseCommand):
    name = 'ensure-indexes'
    help = '''make mongodb indexes'''

    def add_args(self):
        self.add_argument('collections', nargs='*',
                          help='collections to index (default: all')
        self.add_argument('--purge', action='store_true', default=False,
                          help='purge old indexes')

    def handle(self, args):
        all_indexes = {
            'jurisdictions': [
                [('name', ASCENDING)]
            ],
            'organizations': [],
            'people': [],
            'memberships': [
                # get all members for an org
                [('organization_id', ASCENDING), ('end_date', ASCENDING)],
                # get all memberships for a person
                [('person_id', ASCENDING), ('end_date', ASCENDING)],
            ],
            'bills': [],
            'events': [],
            'votes': [],
        }
        api_indexes = {
            'organizations': [
                ['jurisdiction_id'],
                ['classification'],
                ['parent_id'],
                ['division_id'],
                ['identifiers.scheme', 'identifiers.identifier'],
                [],
            ],
            'people': [
                ['identifiers.scheme', 'identifiers.identifier'],
                [],
            ],
            'bills': [
                ['jurisdiction_id'],
                ['identifiers.scheme', 'identifiers.identifier'],
                [],
            ],
            'events': [
                ['jurisdiction_id'],
                ['participants.id'],
                ['agenda.related_entities.id'],
                [],
            ],
            'votes': [
                ['jurisdiction_id'],
                ['session'],
                ['bill.id'],
            ],
        }

        for _type, indexes in api_indexes.items():
            for fields in indexes:
                real_index = zip(fields, itertools.repeat(ASCENDING))
                all_indexes[_type].append(real_index +
                                          [('created_at', DESCENDING)])
                all_indexes[_type].append(real_index +
                                          [('updated_at', DESCENDING)])
                if _type == 'events':
                    all_indexes[_type].append(real_index +
                                              [('when', DESCENDING)])
                if _type == 'date':
                    all_indexes[_type].append(real_index +
                                              [('date', DESCENDING)])

        collections = args.collections or all_indexes.keys()

        for collection in collections:
            print('indexing', collection, '...')
            current = set(db[collection].index_information().keys())
            current.discard('_id_')
            #if collection == 'bills':
                # basic lookup / unique constraint on abbr/session/bill_id
                #current.discard('%s_1_session_1_chamber_1_bill_id_1' %
                #                settings.LEVEL_FIELD)
                #db.bills.ensure_index([
                #    (settings.LEVEL_FIELD, pymongo.ASCENDING),
                #    ('session', pymongo.ASCENDING),
                #    ('chamber', pymongo.ASCENDING),
                #    ('bill_id', pymongo.ASCENDING)
                #], unique=True)
                #print('creating level-session-chamber-bill_id index')
            print('currently has', len(current), 'indexes (not counting _id)')
            print('ensuring', len(all_indexes[collection]), 'indexes')
            ensured = set()
            for index in all_indexes[collection]:
                if isinstance(index, list):
                    ensured.add(db[collection].ensure_index(index))
                elif isinstance(index, dict):
                    name, index_spec = index.items()[0]
                    ensured.add(
                        db[collection].ensure_index(index_spec, name=name))
                else:
                    raise ValueError(index)
            new = ensured - current
            old = current - ensured
            if len(new):
                print(len(new), 'new indexes:', ', '.join(new))
            if len(old):
                print(len(old), 'indexes deprecated:', ', '.join(old))
                if args.purge:
                    print('removing deprecated indexes...')
                    for index in old:
                        db[collection].drop_index(index)
