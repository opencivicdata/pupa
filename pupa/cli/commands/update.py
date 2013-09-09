from __future__ import print_function
import os
import sys
import glob
import importlib
import traceback
from collections import defaultdict
from functools import reduce

from .base import BaseCommand
from pupa import utils

from pupa.importers.jurisdiction import import_jurisdiction
from pupa.importers.organizations import OrganizationImporter
from pupa.importers.people import PersonImporter
from pupa.importers.memberships import MembershipImporter
from pupa.importers.events import EventImporter
from pupa.importers.bills import BillImporter
from pupa.importers.votes import VoteImporter
from pupa.scrape import Jurisdiction


ALL_ACTIONS = ('scrape', 'import', 'report')


class UpdateError(Exception):
    pass


class Command(BaseCommand):
    name = 'update'
    help = 'update pupa data'

    def add_args(self):
        # what to scrape
        self.add_argument('module', type=str, help='path to scraper module')
        for arg in ALL_ACTIONS:
            self.add_argument('--' + arg, dest='actions',
                              action='append_const', const=arg,
                              help='only run {0} post-scrape step'.format(arg))
        for arg in ('people', 'bills', 'events', 'votes', 'speeches'):
            self.add_argument('--' + arg, dest='scrapers',
                              action='append_const', const=arg,
                              help='run {0} scraper'.format(arg))

        self.add_argument('-s', '--session', action='append', dest='sessions',
                          default=[], help='session(s) to scrape')
        self.add_argument('-t', '--term', dest='term', help='term to scrape')

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
            if (getattr(obj, 'jurisdiction_id', None) and
                    issubclass(obj, Jurisdiction)):
                # In the case of top-level scraper classes, the scraper objects
                # will have a jurisdiction_id, but not actually be
                # jurisdictions. As a result, we should ensure all objects we
                # pick up are actually Jurisdiction subclasses.

                return obj()  # instantiate the class

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
            term = juris.terms[-1]['name']
            sessions = juris.terms[-1]['sessions']

        return term, sessions

    def do_scrape(self, juris, args):
        # make output and cache dirs
        utils.makedirs(args.cachedir)
        utils.makedirs(args.datadir)
        # clear json from data dir
        for f in glob.glob(args.datadir + '/*.json'):
            os.remove(f)

        report = {}

        # run scrapers
        for session in args.sessions:
            # get mapping of ScraperClass -> scrapers
            session_scrapers = defaultdict(list)
            for scraper_type in args.scrapers:
                ScraperCls = juris.get_scraper(args.term, session,
                                               scraper_type)
                if not ScraperCls:
                    raise Exception('no scraper for term={0} session={1} '
                                    'type={2}'.format(args.term, session,
                                                      scraper_type))
                session_scrapers[ScraperCls].append(scraper_type)

            report[session] = {}

            # run each scraper once
            for ScraperCls, scraper_types in session_scrapers.items():
                scraper = ScraperCls(juris, session, args.datadir,
                                     args.cachedir, args.strict,
                                     args.fastmode)
                if 'people' in scraper_types:
                    report[session].update(scraper.scrape_people())
                elif 'bills' in scraper_types:
                    report[session].update(scraper.scrape_bills())
                elif 'events' in scraper_types:
                    report[session].update(scraper.scrape_events())
                elif 'votes' in scraper_types:
                    report[session].update(scraper.scrape_votes())
                elif 'speeches' in scraper_types:
                    report[session].update(scraper.scrape_speeches())

        return report

    def do_import(self, juris, args):
        org_importer = OrganizationImporter(juris.jurisdiction_id)
        person_importer = PersonImporter(juris.jurisdiction_id)

        membership_importer = MembershipImporter(juris.jurisdiction_id,
                                                 person_importer,
                                                 org_importer)

        bill_importer = BillImporter(juris.jurisdiction_id)

        vote_importer = VoteImporter(juris.jurisdiction_id,
                                     person_importer,
                                     org_importer,
                                     bill_importer)

        event_importer = EventImporter(juris.jurisdiction_id)

        report = {}

        # XXX: jurisdiction into report
        import_jurisdiction(org_importer, juris)
        report.update(org_importer.import_from_json(args.datadir))
        report.update(person_importer.import_from_json(args.datadir))
        report.update(membership_importer.import_from_json(args.datadir))
        report.update(bill_importer.import_from_json(args.datadir))
        report.update(event_importer.import_from_json(args.datadir))
        report.update(vote_importer.import_from_json(args.datadir))

        return report

    def check_session_list(self, juris):
        sessions = juris.scrape_session_list()

        all_sessions_in_terms = list(
            reduce(lambda x, y: x + y, [x['sessions'] for x in juris.terms])
        )
        # copy the list to avoid modifying it
        session_details = list(juris._ignored_scraped_sessions)

        for k, v in juris.session_details.items():
            try:
                all_sessions_in_terms.remove(k)
            except ValueError:
                raise UpdateError('session {0} exists in session_details but '
                                  'not in a term'.format(k))

            session_details.append(v.get('_scraped_name'))

        if not sessions:
            raise UpdateError('no sessions from scrape_session_list()')

        if all_sessions_in_terms:
            raise UpdateError('no session_details for session(s): %r' %
                              all_sessions_in_terms)

        unaccounted_sessions = []
        for s in sessions:
            if s not in session_details:
                unaccounted_sessions.append(s)
        if unaccounted_sessions:
            raise UpdateError('session(s) unaccounted for: %r' %
                              unaccounted_sessions)

    def handle(self, args):
        self.enable_debug(args.debug)

        juris = self.get_jurisdiction(args.module)

        # modify args in-place so we can pass them around
        if not args.actions:
            args.actions = ALL_ACTIONS
        args.cachedir = os.path.join(args.cachedir, juris.jurisdiction_id)
        args.datadir = os.path.join(args.datadir, juris.jurisdiction_id)

        # terms, sessions, and object types
        args.term, args.sessions = self.get_timespan(juris, args.term,
                                                     args.sessions)
        args.scrapers = args.scrapers or juris.provides

        # print the plan
        print('module:', args.module)
        print('actions:', ', '.join(args.actions))
        print('term:', args.term)
        print('sessions:', ', '.join(args.sessions))
        print('scrapers:', ', '.join(args.scrapers))
        plan = {'module': args.module, 'actions': args.actions,
                'term': args.term, 'sessions': args.sessions,
                'scrapers': args.scrapers}

        report = {'plan': plan}
        if 'scrape' in args.actions:
            self.check_session_list(juris)
            report['scrape'] = self.do_scrape(juris, args)
        if 'import' in args.actions:
            report['import'] = self.do_import(juris, args)

        report['success'] = True

        # XXX: save report instead of printing
        print(report)
