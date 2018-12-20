import os
import glob
import logging
import importlib
import traceback
import contextlib
from collections import OrderedDict

import django
from django.db import transaction

from pupa import utils
from pupa import settings
from pupa.scrape import Jurisdiction, JurisdictionScraper
from pupa.exceptions import CommandError

from .base import BaseCommand


ALL_ACTIONS = ('scrape', 'import')


class _Unset:
    pass


UNSET = _Unset()


@contextlib.contextmanager
def override_settings(settings, overrides):
    original = {}
    for key, value in overrides.items():
        original[key] = getattr(settings, key, UNSET)
        setattr(settings, key, value)
    yield
    for key, value in original.items():
        if value is UNSET:
            delattr(settings, key)
        else:
            setattr(settings, key, value)


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


@transaction.atomic
def save_report(report, jurisdiction):
    from pupa.models import RunPlan
    from opencivicdata.core.models import Jurisdiction as JurisdictionModel

    # set end time
    report['end'] = utils.utcnow()

    # if there's an error on the first run, the jurisdiction doesn't exist
    # yet, we opt for skipping creation of RunPlan until there's been at least
    # one good run
    try:
        JurisdictionModel.objects.get(pk=jurisdiction)
    except JurisdictionModel.DoesNotExist:
        logger = logging.getLogger("pupa")
        logger.warning('could not save RunPlan, no successful runs of {} yet'.format(
            jurisdiction)
        )
        return

    plan = RunPlan.objects.create(jurisdiction_id=jurisdiction,
                                  success=report['success'],
                                  start_time=report['start'],
                                  end_time=report['end'],
                                  exception=report.get('exception', ''),
                                  traceback=report.get('traceback', ''),
                                  )

    for scraper, details in report.get('scrape', {}).items():
        args = ' '.join('{k}={v}'.format(k=k, v=v)
                        for k, v in report['plan']['scrapers'].get(scraper, {}).items())
        sr = plan.scrapers.create(scraper=scraper, args=args,
                                  start_time=details['start'], end_time=details['end'])
        for object_type, num in details['objects'].items():
            sr.scraped_objects.create(object_type=object_type, count=num)

    for object_type, changes in report.get('import', {}).items():
        if changes['insert'] or changes['update'] or changes['noop']:
            plan.imported_objects.create(
                object_type=object_type,
                insert_count=changes['insert'],
                update_count=changes['update'],
                noop_count=changes['noop'],
                start_time=changes['start'],
                end_time=changes['end'],
            )


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
                          help='skip validation on save')
        self.add_argument('--fastmode', action='store_true',
                          help='use cache and turn off throttling')

        # settings overrides
        self.add_argument('--datadir', help='data directory', dest='SCRAPED_DATA_DIR')
        self.add_argument('--cachedir', help='cache directory', dest='CACHE_DIR')
        self.add_argument('-r', '--rpm', help='scraper rpm', type=int, dest='SCRAPELIB_RPM')
        self.add_argument('--timeout', help='scraper timeout', type=int, dest='SCRAPELIB_TIMEOUT')
        self.add_argument('--no-verify', help='skip tls verification',
                          action='store_false', dest='SCRAPELIB_VERIFY')
        self.add_argument('--retries', help='scraper retries', type=int, dest='SCRAPELIB_RETRIES')
        self.add_argument('--retry_wait', help='scraper retry wait', type=int,
                          dest='SCRAPELIB_RETRY_WAIT_SECONDS')

    def get_jurisdiction(self, module_name):
        # get the jurisdiction object
        module = importlib.import_module(module_name)
        for obj in module.__dict__.values():
            # ensure we're dealing with a subclass of Jurisdiction
            if (isinstance(obj, type) and
               issubclass(obj, Jurisdiction) and
               getattr(obj, 'division_id', None) and
               obj.classification):
                return obj(), module
        raise CommandError('Unable to import Jurisdiction subclass from ' +
                           module_name +
                           '. Jurisdiction subclass may be missing a ' +
                           'division_id or classification.')

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
                                    VoteEventImporter, EventImporter)
        from pupa.reports import generate_session_report
        from pupa.models import SessionDataQualityReport
        datadir = os.path.join(settings.SCRAPED_DATA_DIR, args.module)

        juris_importer = JurisdictionImporter(juris.jurisdiction_id)
        org_importer = OrganizationImporter(juris.jurisdiction_id)
        person_importer = PersonImporter(juris.jurisdiction_id)
        post_importer = PostImporter(juris.jurisdiction_id, org_importer)
        membership_importer = MembershipImporter(juris.jurisdiction_id, person_importer,
                                                 org_importer, post_importer)
        bill_importer = BillImporter(juris.jurisdiction_id, org_importer, person_importer)
        vote_event_importer = VoteEventImporter(juris.jurisdiction_id, person_importer,
                                                org_importer, bill_importer)
        event_importer = EventImporter(juris.jurisdiction_id,
                                       org_importer,
                                       person_importer,
                                       bill_importer,
                                       vote_event_importer)

        report = {}

        with transaction.atomic():
            print('import jurisdictions...')
            report.update(juris_importer.import_directory(datadir))
            if settings.ENABLE_PEOPLE_AND_ORGS:
                print('import organizations...')
                report.update(org_importer.import_directory(datadir))
                print('import people...')
                report.update(person_importer.import_directory(datadir))
                print('import posts...')
                report.update(post_importer.import_directory(datadir))
                print('import memberships...')
                report.update(membership_importer.import_directory(datadir))
            if settings.ENABLE_BILLS:
                print('import bills...')
                report.update(bill_importer.import_directory(datadir))
            if settings.ENABLE_EVENTS:
                print('import events...')
                report.update(event_importer.import_directory(datadir))
            if settings.ENABLE_VOTES:
                print('import vote events...')
                report.update(vote_event_importer.import_directory(datadir))

        # compile info on all sessions that were updated in this run
        seen_sessions = set()
        seen_sessions.update(bill_importer.get_seen_sessions())
        seen_sessions.update(vote_event_importer.get_seen_sessions())
        for session in seen_sessions:
            new_report = generate_session_report(session)
            with transaction.atomic():
                SessionDataQualityReport.objects.filter(legislative_session=session).delete()
                new_report.save()

        return report

    def check_session_list(self, juris):
        # if get_session_list is not defined, let it slide
        if not hasattr(juris, "get_session_list"):
            print("Not checking sessions...")
            return

        scraper = type(juris).__name__
        scraped_sessions = juris.get_session_list()

        if not scraped_sessions:
            raise CommandError('no sessions from {}.get_session_list()'.format(scraper))

        # copy the list to avoid modifying it
        sessions = set(juris.ignored_scraped_sessions)
        for session in juris.legislative_sessions:
            sessions.add(session.get('_scraped_name', session['identifier']))

        unaccounted_sessions = list(set(scraped_sessions) - sessions)
        if unaccounted_sessions:
            raise CommandError(
                (
                    'Session(s) {sessions} were reported by {scraper}.get_session_list() '
                    'but were not found in {scraper}.legislative_sessions or '
                    '{scraper}.ignored_scraped_sessions.'
                ).format(
                    sessions=', '.join(unaccounted_sessions),
                    scraper=scraper,
                )
            )

    def handle(self, args, other):
        juris, module = self.get_jurisdiction(args.module)
        overrides = {}
        overrides.update(getattr(module, 'settings', {}))
        overrides.update({
            key: value for key, value in vars(args).items()
            if value is not None
        })
        with override_settings(settings, overrides):
            return self.do_handle(args, other, juris)

    def do_handle(self, args, other, juris):

        available_scrapers = getattr(juris, 'scrapers', {})
        default_scrapers = getattr(juris, 'default_scrapers', None)
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
        elif default_scrapers is not None:
            scrapers = {s: {} for s in default_scrapers}
        else:
            scrapers = {key: {} for key in available_scrapers.keys()}

        # modify args in-place so we can pass them around
        if not args.actions:
            args.actions = ALL_ACTIONS

        if 'import' in args.actions:
            django.setup()

        # print the plan
        report = {'plan': {'module': args.module, 'actions': args.actions, 'scrapers': scrapers},
                  'start': utils.utcnow(),
                  }
        print_report(report)

        if 'scrape' in args.actions:
            self.check_session_list(juris)

        try:
            if 'scrape' in args.actions:
                report['scrape'] = self.do_scrape(juris, args, scrapers)
            if 'import' in args.actions:
                report['import'] = self.do_import(juris, args)
            report['success'] = True
        except Exception as exc:
            report['success'] = False
            report['exception'] = exc
            report['traceback'] = traceback.format_exc()
            if 'import' in args.actions:
                save_report(report, juris.jurisdiction_id)
            raise

        if 'import' in args.actions:
            save_report(report, juris.jurisdiction_id)

        print_report(report)
        return report
