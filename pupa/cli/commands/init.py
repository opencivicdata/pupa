from __future__ import print_function
import shutil
import os
from six.moves import input

from .base import BaseCommand, CommandError


def prompt(ps, default=''):
    return input(ps).strip() or default


def write_jurisdiction_template(dirname, short_name, jurisdiction_id, long_name, url,
                                scraper_types):
    camel_case = short_name.title().replace(' ', '')

    # write __init__
    lines = ['from pupa.scrape import Jurisdiction']
    for stype in scraper_types:
        lines.append('from .{} import {}{}Scraper'.format(stype, camel_case, stype.title()))
    lines.append('')
    lines.append('')
    lines.append('class {}(Jurisdiction):'.format(camel_case))
    lines.append('    jurisdiction_id = "{}"'.format(jurisdiction_id))
    lines.append('    name = "{}"'.format(long_name))
    lines.append('    url = "{}"'.format(url))
    lines.append('    scrapers = {')
    for stype in scraper_types:
        lines.append('        "{}": {}{}Scraper,'.format(stype, camel_case, stype.title()))
    lines.append('    }')

    with open(os.path.join(dirname, '__init__.py'), 'w') as of:
        of.write('\n'.join(lines))

    # write scraper files
    for stype in scraper_types:
        classname = {'events': 'Event', 'people': 'Person',
                     'bills': 'Bill', 'votes': 'Vote'}[stype]
        lines = ['from pupa.scrape import Scraper']
        lines.append('from pupa.models import {}'.format(classname))
        lines.append('')
        lines.append('')
        lines.append('class {}{}Scraper(Scraper):'.format(camel_case, stype.title()))
        lines.append('')
        lines.append('    def scrape(self):')
        lines.append('        # needs to be implemented')
        lines.append('        pass')
        with open(os.path.join(dirname, stype + '.py'), 'w') as of:
            of.write('\n'.join(lines))


class Command(BaseCommand):
    name = 'init'
    help = 'start a new pupa scraper'

    def add_args(self):
        self.add_argument('module', type=str, help='name of the new scraper module')

    def handle(self, args, other):
        if os.path.exists(args.module):
            raise CommandError(args.module + ' already exists')
        os.makedirs(args.module)

        short_name = prompt('short name (e.g. Cary): ')
        jurisdiction = prompt('jurisdiction id (e.g. ocd-jurisdiction/country:us/state:nc/place:cary/council): ')
        long_name = prompt('long name (e.g. Cary Town Council): ')
        url = prompt('official URL: ')

        # will default to True until they pick one, then defaults to False
        scraper_types = ('people', 'events', 'bills', 'votes')
        selected_scraper_types = []
        for stype in scraper_types:
            prompt_str = 'create {} scraper? {}: '.format(
                stype, '[y/N]' if selected_scraper_types else '[Y/n]')
            default = 'N' if selected_scraper_types else 'Y'
            result = prompt(prompt_str, default).upper()
            if result == 'Y':
                selected_scraper_types.append(stype)

        write_jurisdiction_template(args.module, short_name, jurisdiction, long_name, url,
                                    selected_scraper_types)
