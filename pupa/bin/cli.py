import argparse
import logging
import importlib

logging.basicConfig()
logger = logging.getLogger('pupa')

COMMAND_MODULES = (
    'pupa.bin.commands.update',
)


def main():
    parser = argparse.ArgumentParser(description='pupa CLI')
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
    #XXX: kernel.update_settings(args)
    subcommands[args.subcommand].handle(args)

if __name__ == '__main__':
    main()
