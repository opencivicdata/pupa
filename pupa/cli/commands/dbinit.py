import django
from django.db import connection
from django.core.management import call_command

from .base import BaseCommand


def copy_tmp(tablename):
    cursor = connection.cursor()
    print('copying data from table ' + tablename)
    cursor.execute("DROP TABLE IF EXISTS tmp_{t};".format(t=tablename))
    cursor.execute("CREATE TABLE tmp_{t} (LIKE {t});".format(t=tablename))
    cursor.execute("INSERT INTO tmp_{t} SELECT * FROM {t};".format(t=tablename))


def restore_from_tmp(tablename):
    print('restoring data to table ' + tablename)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO {t} SELECT * FROM tmp_{t};".format(t=tablename))
    cursor.execute("DROP TABLE IF EXISTS tmp_{t};".format(t=tablename))


def drop_tables(skip_divisions=False):
    tables = connection.introspection.table_names()
    cursor = connection.cursor()
    for table in tables:
        if table.startswith(('opencivicdata_', 'pupa_')):
            print('dropping table ' + table)
            cursor.execute("DROP TABLE IF EXISTS {} CASCADE;".format(table))
        cursor.execute("DELETE FROM django_migrations WHERE app='core';")
        cursor.execute("DELETE FROM django_migrations WHERE app='legislative';")
        cursor.execute("DELETE FROM django_migrations WHERE app='pupa';")


class Command(BaseCommand):
    name = 'dbinit'
    help = 'initialize a pupa database'

    def add_args(self):
        self.add_argument('--reset', action='store_true', default=False,
                          help='reset entire database - USE WITH CAUTION')
        self.add_argument('--partial-reset', action='store_true', default=False,
                          help='reset entire database, except for divisions - USE WITH CAUTION')
        self.add_argument(type=str, dest='country', nargs='+',
                          help='country to load divisions for')

    def handle(self, args, other):
        django.setup()

        if args.partial_reset:
            copy_tmp('opencivicdata_division')
            drop_tables()
        elif args.reset:
            drop_tables()
        else:
            pass

        call_command('migrate', interactive=False)

        if args.partial_reset:
            restore_from_tmp('opencivicdata_division')
        else:
            for country in args.country:
                call_command('loaddivisions', country)
