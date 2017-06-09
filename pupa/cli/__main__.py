import os
import sys
import logging.config
import argparse
import importlib
import traceback
from django.conf import settings
from pupa.exceptions import CommandError

logger = logging.getLogger('pupa')

COMMAND_MODULES = (
    'pupa.cli.commands.init',
    'pupa.cli.commands.dbinit',
    'pupa.cli.commands.update',
    'pupa.cli.commands.party',
)


def main():
    parser = argparse.ArgumentParser('pupa', description='pupa CLI')
    parser.add_argument('--debug', action='store_true',
                        help='open debugger on error')
    parser.add_argument('--loglevel', default='INFO', help=('set log level. options are: '
                                                            'DEBUG|INFO|WARNING|ERROR|CRITICAL '
                                                            '(default is INFO)'))
    subparsers = parser.add_subparsers(dest='subcommand')

    # configure Django before model imports
    if os.environ.get("DJANGO_SETTINGS_MODULE") is None:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'pupa.settings'

    subcommands = {}
    for mod in COMMAND_MODULES:
        try:
            cmd = importlib.import_module(mod).Command(subparsers)
            subcommands[cmd.name] = cmd
        except ImportError as e:
            logger.error('exception "%s" prevented loading of %s module', e, mod)

    # process args
    args, other = parser.parse_known_args()

    # set log level from command line
    handler_level = getattr(logging, args.loglevel.upper(), 'INFO')
    settings.LOGGING['handlers']['default']['level'] = handler_level
    logging.config.dictConfig(settings.LOGGING)

    # turn debug on
    if args.debug:
        try:
            debug_module = importlib.import_module('ipdb')
        except ImportError:
            debug_module = importlib.import_module('pdb')

        # turn on PDB-on-error mode
        # stolen from http://stackoverflow.com/questions/1237379/
        # if this causes problems in interactive mode check that page
        def _tb_info(type, value, tb):
            traceback.print_exception(type, value, tb)
            debug_module.pm()
        sys.excepthook = _tb_info

    if not args.subcommand:
        parser.print_help()
    else:
        try:
            subcommands[args.subcommand].handle(args, other)
        except CommandError as e:
            logger.critical(str(e))
            sys.exit(1)


if __name__ == '__main__':
    main()
