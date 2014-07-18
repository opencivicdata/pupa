import os
import glob
import importlib
from collections import OrderedDict

from django.db import transaction

from .base import BaseCommand, CommandError
from pupa import settings, utils
from pupa.scrape import Jurisdiction, JurisdictionScraper


ALL_ACTIONS = ('scrape', 'import', 'report')


def print_report(report):
    plan = report['plan']
    print('{} ({})'.format(plan['module'], ', '.join(plan['actions'])))
    for scraper, args in plan['scrapers'].items():
        print('  {}: {}'.format(scraper, args))
    if 'scrape' in report:
        for type, details in sorted(report['scrape'].items()):
            print(type + ' scrape:')
            print('  duration: ', (details['end'] - details['start']))
            print('  objects:')
            for objtype, num in sorted(details['objects'].items()):
                print('    {}: {}'.format(objtype, num))
    if 'import' in report:
        print('import:')
        for type, changes in sorted(report['import'].items()):
            if(changes['insert'] or changes['update'] or changes['noop']):
                print('  {}: {} new {} updated {} noop'.format(type, changes['insert'],
                                                               changes['update'], changes['noop']))


class Command(BaseCommand):
    name = 'update'
    help = 'update pupa data'

    def add_args(self):
        # what to scrape
        self.add_argument('module', type=str, help='path to scraper module')
        for arg in ALL_ACTIONS:
            self.add_argument('--' + arg, dest='actions', action='append_const', const=arg,
                              help='only run {} post-scrape step'.format(arg))

        # scraper arguments
        self.add_argument('--nonstrict', action='store_false', dest='strict',
                          default=True, help='skip validation on save')
        self.add_argument('--fastmode', action='store_true', default=False,
                          help='use cache and turn off throttling')

        # settings overrides
        self.add_argument('--datadir', help='data directory', dest='SCRAPED_DATA_DIR')
        self.add_argument('--cachedir', help='cache directory', dest='CACHE_DIR')
        self.add_argument('-r', '--rpm', help='scraper rpm', type=int, dest='SCRAPELIB_RPM')
        self.add_argument('--timeout', help='scraper timeout', type=int, dest='SCRAPELIB_TIMEOUT')
        self.add_argument('--retries', help='scraper retries', type=int, dest='SCRAPELIB_RETRIES')
        self.add_argument('--retry_wait', help='scraper retry wait', type=int,
                          dest='SCRAPELIB_RETRY_WAIT_SECONDS')

    def get_jurisdiction(self, module_name):
        # get the jurisdiction object
        module = importlib.import_module(module_name)
        for obj in module.__dict__.values():
            # ensure we're sealing with a subclass of Jurisdiction
            if isinstance(obj, type) and issubclass(obj, Jurisdiction):
                if obj == Jurisdiction:
                    # We're looking at the imported Jurisdiction.
                    continue
                if getattr(obj, 'division_id', None):
                    if obj.classification is None:
                        raise CommandError(
                            "classification isn't set on '"
                            + obj.__name__ + "'"
                        )
                    return obj()
                else:
                    raise CommandError("Jurisdiction subclass '" + obj.__name__
                                       + "' is missing a division_id")
        raise CommandError('unable to import Jurisdiction subclass from ' + module_name)

    def do_scrape(self, juris, args, scrapers):
        # make output and cache dirs
        utils.makedirs(settings.CACHE_DIR)
        datadir = os.path.join(settings.SCRAPED_DATA_DIR, args.module)
        utils.makedirs(datadir)
        # clear json from data dir
        for f in glob.glob(datadir + '/*.json'):
            os.remove(f)

        report = {}

        # do jurisdiction
        jscraper = JurisdictionScraper(juris, datadir, strict_validation=args.strict,
                                       fastmode=args.fastmode)
        report['jurisdiction'] = jscraper.do_scrape()

        for scraper_name, scrape_args in scrapers.items():
            ScraperCls = juris.scrapers[scraper_name]
            scraper = ScraperCls(juris, datadir, strict_validation=args.strict,
                                 fastmode=args.fastmode)
            report[scraper_name] = scraper.do_scrape(**scrape_args)

        return report

    def do_import(self, juris, args):
        # import inside here because to avoid loading Django code unnecessarily
        from pupa.importers import (JurisdictionImporter, OrganizationImporter, PersonImporter,
                                    PostImporter, MembershipImporter, BillImporter,
                                    VoteImporter, EventImporter)
        datadir = os.path.join(settings.SCRAPED_DATA_DIR, args.module)

        juris_importer = JurisdictionImporter(juris.jurisdiction_id)
        org_importer = OrganizationImporter(juris.jurisdiction_id)
        person_importer = PersonImporter(juris.jurisdiction_id)
        post_importer = PostImporter(juris.jurisdiction_id, org_importer)
        membership_importer = MembershipImporter(juris.jurisdiction_id, person_importer,
                                                 org_importer, post_importer)
        bill_importer = BillImporter(juris.jurisdiction_id, org_importer)
        vote_importer = VoteImporter(juris.jurisdiction_id, person_importer, org_importer,
                                     bill_importer)
        event_importer = EventImporter(juris.jurisdiction_id)

        report = {}

        with transaction.atomic():
            print('import jurisdictions...')
            report.update(juris_importer.import_directory(datadir))
            print('import organizations...')
            report.update(org_importer.import_directory(datadir))
            print('import people...')
            report.update(person_importer.import_directory(datadir))
            print('import posts...')
            report.update(post_importer.import_directory(datadir))
            print('import memberships...')
            report.update(membership_importer.import_directory(datadir))
            print('import bills...')
            report.update(bill_importer.import_directory(datadir))
            print('import events...')
            report.update(event_importer.import_directory(datadir))
            print('import votes...')
            report.update(vote_importer.import_directory(datadir))

        return report

    def check_session_list(self, juris):
        scraped_sessions = juris.scrape_session_list()

        if not scraped_sessions:
            raise CommandError('no sessions from scrape_session_list()')

        # copy the list to avoid modifying it
        sessions = list(juris.ignored_scraped_sessions)
        # add _scraped_names
        for session in juris.legislative_sessions:
            sn = session.get('_scraped_name')
            if sn:
                sessions.append(sn)

        unaccounted_sessions = list(set(scraped_sessions) - set(sessions))
        if unaccounted_sessions:
            raise CommandError('session(s) unaccounted for: %s' % ', '.join(unaccounted_sessions))

    def handle(self, args, other):
        juris = self.get_jurisdiction(args.module)

        available_scrapers = getattr(juris, 'scrapers', {})
        scrapers = OrderedDict()

        if not available_scrapers:
            raise CommandError('no scrapers defined on jurisdiction')

        if other:
            # parse arg list in format: (scraper (k:v)+)+
            cur_scraper = None
            for arg in other:
                if '=' in arg:
                    if not cur_scraper:
                        raise CommandError('argument {} before scraper name'.format(arg))
                    k, v = arg.split('=', 1)
                    scrapers[cur_scraper][k] = v
                elif arg in juris.scrapers:
                    cur_scraper = arg
                    scrapers[cur_scraper] = {}
                else:
                    raise CommandError('no such scraper: module={} scraper={}'.format(args.module,
                                                                                      arg))
        else:
            scrapers = {key: {} for key in available_scrapers.keys()}

        # modify args in-place so we can pass them around
        if not args.actions:
            args.actions = ALL_ACTIONS

        # print the plan
        report = {'plan': {'module': args.module, 'actions': args.actions, 'scrapers': scrapers}}
        print_report(report)

        if 'scrape' in args.actions:
            report['scrape'] = self.do_scrape(juris, args, scrapers)
        if 'import' in args.actions:
            report['import'] = self.do_import(juris, args)

        report['success'] = True

        # XXX: save report
        print_report(report)
        return report
