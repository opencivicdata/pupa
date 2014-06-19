from __future__ import print_function

from django.db import connection
from django.core.management import call_command

from .base import BaseCommand


def drop_tables():
    tables = connection.introspection.table_names()
    cursor = connection.cursor()
    for table in tables:
        if table.startswith('opencivicdata_'):
            print('dropping table ' + table)
            cursor.execute("DROP TABLE IF EXISTS {} CASCADE;".format(table))
        cursor.execute("DELETE FROM django_migrations WHERE app='opencivicdata';")


class Command(BaseCommand):
    name = 'dbinit'
    help = 'initialize a pupa database'

    def add_args(self):
        self.add_argument('--reset', action='store_true', default=False,
                          help='reset entire database - USE WITH CAUTION')
        self.add_argument(type=str, dest='country', nargs='+',
                          help='country to load divisions for')

    def handle(self, args, other):
        if args.reset:
            drop_tables()
        call_command('migrate', interactive=False)
        for country in args.country:
            call_command('loaddivisions', country)
