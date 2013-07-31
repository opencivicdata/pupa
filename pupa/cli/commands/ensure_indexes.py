from __future__ import print_function
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
            'metadata': [
                [('name', ASCENDING)]
            ],
            'organizations': [
                [('classification', ASCENDING), ('created_at', DESCENDING) ],
                [('jurisdiction_id', ASCENDING), ('created_at', DESCENDING) ],
                [('parent_id', ASCENDING), ('created_at', DESCENDING) ],
                [('division_id', ASCENDING), ('created_at', DESCENDING) ],
                [('identifiers.scheme', ASCENDING),
                 ('identifiers.identifier', ASCENDING),
                 ('created_at', DESCENDING) ],
                [('created_at', DESCENDING) ],
            ],
            'people': [
                #[('division_id', ASCENDING), ('created_at', DESCENDING) ],
                [('identifiers.scheme', ASCENDING),
                 ('identifiers.identifier', ASCENDING),
                 ('created_at', DESCENDING) ],
                [('updated_at', DESCENDING) ],
                [('created_at', DESCENDING) ],
            ],
            'memberships': [
                [('organization_id', ASCENDING), ('end_date', ASCENDING)],
                [('person_id', ASCENDING), ('end_date', ASCENDING)],
            ],
            'bills': [
                [('created_at', DESCENDING) ],
            ],
            'events': [
                [('created_at', DESCENDING) ],
            ],
            'votes': [
                [('created_at', DESCENDING) ],
            ],
        }

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
