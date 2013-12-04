#!/usr/bin/env python
from pupa.utils import JSONEncoderPlus
from contextlib import contextmanager
from pymongo import Connection
import argparse
import json
import os

parser = argparse.ArgumentParser(description='Re-convert a jurisdiction.')

parser.add_argument('--server', type=str, help='Mongo Server',
                    default="localhost")

parser.add_argument('--database', type=str, help='Mongo Database',
                    default="opencivicdata")

parser.add_argument('--port', type=int, help='Mongo Server Port',
                    default=27017)

parser.add_argument('--output', type=str, help='Output Directory',
                    default="dump")

parser.add_argument('root', type=str, help='root', default='dump')

args = parser.parse_args()


connection = Connection(args.server, args.port)
db = getattr(connection, args.database)
jurisdiction = args.jurisdiction


@contextmanager
def cd(path):
    pop = os.getcwd()
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(pop)


with cd(args.root):
    print os.getcwd()
