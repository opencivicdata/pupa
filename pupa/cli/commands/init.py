from __future__ import print_function
import shutil
from os.path import join, abspath, dirname

from .base import BaseCommand


class UpdateError(Exception):
    pass


class Command(BaseCommand):
    name = 'init'
    help = 'start a new pupa scraper'

    def add_args(self):
        # what to scrape
        self.add_argument('module', type=str, help='name of the new scraper module')

        # debugging
        self.add_argument('--debug', nargs='?', const='pdb', default=None,
                          help='drop into pdb (or set =ipdb =pudb)')

    def enable_debug(self, debug):
        # turn debug on
        if debug:
            _debugger = importlib.import_module(debug)

            # turn on PDB-on-error mode
            # stolen from http://stackoverflow.com/questions/1237379/
            # if this causes problems in interactive mode check that page
            def _tb_info(type, value, tb):
                traceback.print_exception(type, value, tb)
                _debugger.pm()
            sys.excepthook = _tb_info

    def handle(self, args):
        self.enable_debug(args.debug)
        pupa_dir = dirname(abspath(__file__))
        example_dir = join(pupa_dir, '../../../example')
        ignore = shutil.ignore_patterns('*.pyc', '__pycache__')
        shutil.copytree(example_dir, args.module, ignore=ignore)
