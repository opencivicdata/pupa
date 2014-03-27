from __future__ import print_function
import shutil
from os.path import join, abspath, dirname

from .base import BaseCommand


class Command(BaseCommand):
    name = 'init'
    help = 'start a new pupa scraper'

    def add_args(self):
        # what to scrape
        self.add_argument('module', type=str, help='name of the new scraper module')

    def handle(self, args):
        pupa_dir = dirname(abspath(__file__))
        example_dir = join(pupa_dir, '../../../example')
        ignore = shutil.ignore_patterns('*.pyc', '__pycache__')
        try:
            shutil.copytree(example_dir, args.module, ignore=ignore)
        except OSError as exc:
            if exc.errno:
                print('Error: the folder %r already exists.' % args.module)
