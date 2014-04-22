from __future__ import print_function
import os
import csv
from subprocess import check_call

from django.db import transaction, connection
from django.core.management import call_command

from .base import BaseCommand, CommandError
from pupa.models import Division

OCDID_REPO = 'https://github.com/opencivicdata/ocd-division-ids.git'
LOCAL_REPO = '/tmp/ocdids'


def checkout_repo():
    """ either checkout or update the LOCAL_REPO """
    if os.path.exists(LOCAL_REPO):
        cwd = os.getcwd()
        os.chdir(LOCAL_REPO)
        check_call(['git', 'pull'])
        os.chdir(cwd)
    else:
        check_call(['git', 'clone', OCDID_REPO, LOCAL_REPO])


def drop_tables():
    tables = connection.introspection.table_names()
    cursor = connection.cursor()
    for table in tables:
        if table.startswith('pupa_'):
            print('dropping table ' + table)
            cursor.execute("DROP TABLE IF EXISTS {} CASCADE;".format(table))


def _ocd_id_to_args(ocd_id):
    pieces = ocd_id.split('/')
    if pieces.pop(0) != 'ocd-division':
        raise Exception('ID must start with ocd-division/')
    country = pieces.pop(0)
    if not country.startswith('country:'):
        raise Exception('Second part of ID must be country:')
    else:
        country = country.replace('country:', "")
    n = 1
    args = {'country': country}
    for piece in pieces:
        type_, id_ = piece.split(':')
        args['subtype%s' % n] = type_
        args['subid%s' % n] = id_
        n += 1
    return args


def load_divisions(country):
    count = 0
    filename = os.path.join(LOCAL_REPO, 'identifiers', 'country-{}.csv'.format(country))
    print('loading ' + filename)

    objects = []
    # country csv
    for row in csv.DictReader(open(filename, encoding='utf8')):
        args = _ocd_id_to_args(row['id'])
        args['redirect_id'] = row.get('sameAs', None) or None
        objects.append(Division(id=row['id'], display_name=row['name'], **args))

    print(len(objects), 'divisions loaded from CSV')

    # delete old ids and add new ones all at once
    with transaction.atomic():
        Division.objects.filter(country=country).delete()
        Division.objects.bulk_create(objects, batch_size=10000)

    print(len(objects), 'divisions created')


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
        checkout_repo()
        for country in args.country:
            load_divisions(country)
