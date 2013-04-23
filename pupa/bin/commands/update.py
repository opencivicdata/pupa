import os
import sys
import glob
import importlib
import traceback
from collections import defaultdict

from .base import BaseCommand
from pupa import utils


class UpdateError(Exception):
    pass


class Command(BaseCommand):
    name = 'update'
    help = 'update pupa data'

    def add_args(self):
        # what to scrape
        self.add_argument('module', type=str, help='path to scraper module')
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

    def get_org(self, module):
        # get the org object
        module = importlib.import_module(module + '.organization')
        for obj in module.__dict__.values():
            if getattr(obj, 'organization_id', None):
                # instantiate the class
                return obj()

        raise UpdateError('unable to import Organization subclass from ' +
                          module + '.organization')

    def get_timespan(self, org, term, sessions):
        if term and sessions:
            raise UpdateError('cannot specify both --term and --session')
        elif sessions:
            terms = set()
            for sess in sessions:
                terms.add(org.term_for_session(sess))
            if len(terms) != 1:
                raise UpdateError('cannot scrape sessions across terms')
            term = terms.pop()
        elif term:
            sessions = org.get_term_details(term)['sessions']
        else:
            term = org.metadata['terms'][-1]['name']
            sessions = org.metadata['terms'][-1]['sessions']

        return term, sessions

    def handle(self, args):
        self.enable_debug(args.debug)

        org = self.get_org(args.module)

        # get terms, sessions, and object types
        term, sessions = self.get_timespan(org, args.term, args.sessions)
        obj_types = args.obj_types or org.metadata['provides']

        # make output and cache dirs
        cache_dir = os.path.join(args.cachedir, org.metadata['id'])
        utils.makedirs(cache_dir)
        data_dir = os.path.join(args.datadir, org.metadata['id'])
        utils.makedirs(data_dir)
        # clear data dirs
        for obj_type in obj_types:
            for f in glob.glob('{0}/{1}*.json'.format(data_dir, obj_type)):
                os.remove(f)

        print('term:', term)
        print('sessions:', sessions)
        print('obj_types:', obj_types)

        # run scrapers
        for session in sessions:
            # get mapping of ScraperClass -> obj_types
            session_scrapers = defaultdict(list)
            for obj_type in obj_types:
                ScraperCls = org.get_scraper(term, session, obj_type)
                if not ScraperCls:
                    raise Exception('no scraper for term={0} session={1}'
                                    'type={2}'.format(term, session, obj_type))
                session_scrapers[ScraperCls].append(obj_type)

            # run each scraper once
            for ScraperCls, scraper_obj_types in session_scrapers.iteritems():
                scraper = ScraperCls(org, session, data_dir, cache_dir,
                                     args.strict, args.fastmode)
                scraper.scrape_types(scraper_obj_types)
