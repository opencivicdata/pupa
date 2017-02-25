import django
from django.db import connection
from django.core.management import call_command

from .base import BaseCommand


class Command(BaseCommand):
    name = 'migrate'
    help = 'migrate a pupa database'

    def handle(self, args, other):
        django.setup()

        call_command('migrate', interactive=True)
