import django
from .base import BaseCommand
from pupa.exceptions import CommandError


class Command(BaseCommand):
    name = 'party'
    help = 'command line tool to manage parties'

    def add_args(self):
        self.add_argument('action', type=str, help='add|list')
        self.add_argument('party_name', type=str, nargs='?')

    def handle(self, args, other):
        django.setup()
        from opencivicdata.core.models import Organization

        if args.action == 'add':
            o, created = Organization.objects.get_or_create(name=args.party_name,
                                                            classification='party')
            if created:
                print('added {}'.format(o))
            else:
                print('{} already exists'.format(o))
        elif args.action == 'list':
            for party in Organization.objects.filter(classification='party').order_by('name'):
                print(party.name)
        else:
            raise CommandError('party action must be "add" or "list"')
