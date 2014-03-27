import argparse
import logging
import importlib

logging.basicConfig()
logger = logging.getLogger('pupa')

COMMAND_MODULES = (
    'pupa.cli.commands.update',
    'pupa.cli.commands.ensure_indexes',
    'pupa.cli.commands.init',
    'pupa.cli.commands.import_billy',
    'pupa.cli.commands.dump',
)


def main():
    parser = argparse.ArgumentParser('pupa', description='pupa CLI')
    subparsers = parser.add_subparsers(dest='subcommand')

    subcommands = {}
    for mod in COMMAND_MODULES:
        try:
            cmd = importlib.import_module(mod).Command(subparsers)
            subcommands[cmd.name] = cmd
        except ImportError as e:
            logger.warning('error "%s" prevented loading of %s module',
                           e, mod)

    # process args
    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
    else:
        subcommands[args.subcommand].handle(args)


if __name__ == '__main__':
    main()
