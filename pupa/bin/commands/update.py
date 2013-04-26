from __future__ import print_function
import os
import sys
import glob
import importlib
import traceback
from collections import defaultdict

from .base import BaseCommand
from pupa import utils

from pupa.importers.jurisdiction import import_jurisdiction
from pupa.importers.organizations import OrganizationImporter
from pupa.importers.people import PersonImporter
from pupa.importers.memberships import MembershipImporter


class UpdateError(Exception):
    pass


class Command(BaseCommand):
    name = 'update'
    help = 'update pupa data'

    def add_args(self):
        # what to scrape
        self.add_argument('module', type=str, help='path to scraper module')
        for arg in ('scrape', 'import'):
            self.add_argument('--' + arg, dest='actions',
                              action='append_const', const=arg,
                              help='only run {0} step'.format(arg))
        self.add_argument('-s', '--session', action='append', dest='sessions',
                          default=[], help='session(s) to scrape')
        self.add_argument('-t', '--term', dest='term', help='term to scrape')
        self.add_argument('-o', '--objects', dest='obj_types', action='append',
                          default=[], help='object types to scrape')

        # debugging
        self.add_argument('--debug', nargs='?', const='pdb', default=None,
                          help='drop into pdb (or set =ipdb =pudb)')

        # scraper arguments
        self.add_argument('--datadir', help='data directory',
                          default=os.path.join(os.getcwd(), 'scraped_data'))
        self.add_argument('--cachedir', help='cache directory',
                          default=os.path.join(os.getcwd(), 'scrape_cache'))
        self.add_argument('--nonstrict', action='store_false', dest='strict',
                          default=True, help='skip validation on save')
        self.add_argument('--fastmode', action='store_true', default=False,
                          help='use cache and turn off throttling')
        self.add_argument('-r', '--rpm', help='scrapelib rpm', type=int,
                          dest='SCRAPELIB_RPM')
        self.add_argument('--timeout', help='scrapelib timeout', type=int,
                          dest='SCRAPELIB_TIMEOUT')
        self.add_argument('--retries', help='scrapelib retries', type=int,
                          dest='SCRAPELIB_RETRIES')
        self.add_argument('--retry_wait', help='scrapelib retry wait',
                          type=int, dest='SCRAPELIB_RETRY_WAIT_SECONDS')

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

    def get_jurisdiction(self, module_name):
        # get the jurisdiction object
        module = importlib.import_module(module_name)
        for obj in module.__dict__.values():
            if getattr(obj, 'jurisdiction_id', None):
                # instantiate the class
                return obj()

        raise UpdateError('unable to import Jurisdiction subclass from ' +
                          module_name)

    def get_timespan(self, juris, term, sessions):
        if term and sessions:
            raise UpdateError('cannot specify both --term and --session')
        elif sessions:
            terms = set()
            for sess in sessions:
                terms.add(juris.term_for_session(sess))
            if len(terms) != 1:
                raise UpdateError('cannot scrape sessions across terms')
            term = terms.pop()
        elif term:
            sessions = juris.get_term_details(term)['sessions']
        else:
            term = juris.metadata['terms'][-1]['name']
            sessions = juris.metadata['terms'][-1]['sessions']

        return term, sessions

    def do_scrape(self, juris, args):
        # make output and cache dirs
        utils.makedirs(args.cachedir)
        utils.makedirs(args.datadir)
        # clear json from data dir
        for f in glob.glob(args.datadir + '/*.json'):
            os.remove(f)

        # run scrapers
        for session in args.sessions:
            # get mapping of ScraperClass -> obj_types
            session_scrapers = defaultdict(list)
            for obj_type in args.obj_types:
                ScraperCls = juris.get_scraper(args.term, session, obj_type)
                if not ScraperCls:
                    raise Exception('no scraper for term={0} session={1} '
                                    'type={2}'.format(args.term, session,
                                                      obj_type))
                session_scrapers[ScraperCls].append(obj_type)

            # run each scraper once
            for ScraperCls, scraper_obj_types in session_scrapers.iteritems():
                scraper = ScraperCls(juris, session, args.datadir,
                                     args.cachedir, args.strict,
                                     args.fastmode)
                scraper.scrape_types(scraper_obj_types)

    def do_import(self, juris, args):
        org_importer = OrganizationImporter(juris.jurisdiction_id)
        person_importer = PersonImporter(juris.jurisdiction_id)
        membership_importer = MembershipImporter(juris.jurisdiction_id,
                                                 person_importer,
                                                 org_importer)
        import_jurisdiction(org_importer, juris)
        org_importer.import_from_json(args.datadir)
        person_importer.import_from_json(args.datadir)
        membership_importer.import_from_json(args.datadir)

    def handle(self, args):
        self.enable_debug(args.debug)

        juris = self.get_jurisdiction(args.module)

        # modify args in-place so we can pass them around
        if not args.actions:
            args.actions = ('scrape', 'import')
        args.cachedir = os.path.join(args.cachedir, juris.jurisdiction_id)
        args.datadir = os.path.join(args.datadir, juris.jurisdiction_id)

        # terms, sessions, and object types
        args.term, args.sessions = self.get_timespan(juris, args.term,
                                                     args.sessions)
        args.obj_types = args.obj_types or juris.metadata['provides']

        # print the plan
        print('module:', args.module)
        print('actions:', ', '.join(args.actions))
        print('term:', args.term)
        print('sessions:', ', '.join(args.sessions))
        print('obj_types:', ', '.join(args.obj_types))

        if 'scrape' in args.actions:
            self.do_scrape(juris, args)
        if 'import' in args.actions:
            self.do_import(juris, args)
