import os
import sys

from .base import BaseCommand, CommandError
from opencivicdata.common import JURISDICTION_CLASSIFICATIONS
from opencivicdata.divisions import Division

def prompt(ps, default=''):
    return input(ps).strip() or default

CLASS_DICT = {'events': 'Event',
              'people': 'Person',
              'bills': 'Bill',
              'votes': 'Vote'}


def write_jurisdiction_template(dirname, short_name, long_name, division_id, classification, url,
                                scraper_types):
    camel_case = short_name.title().replace(' ', '')

    # write __init__
    lines = ['# encoding=utf-8', 'from pupa.scrape import Jurisdiction, Organization']
    for stype in scraper_types:
        lines.append('from .{} import {}{}Scraper'.format(stype, camel_case, CLASS_DICT[stype]))
    lines.append('')
    lines.append('')
    lines.append('class {}(Jurisdiction):'.format(camel_case))
    lines.append('    division_id = "{}"'.format(division_id))
    lines.append('    classification = "{}"'.format(classification))
    lines.append('    name = "{}"'.format(long_name))
    lines.append('    url = "{}"'.format(url))
    lines.append('    scrapers = {')
    for stype in scraper_types:
        lines.append('        "{}": {}{}Scraper,'.format(stype, camel_case, CLASS_DICT[stype]))
    lines.append('    }')
    lines.append('')
    lines.append('    def get_organizations(self):')
    lines.append('        #REQUIRED: define an organization using this format')
    lines.append('        #where org_name is something like Seattle City Council')
    lines.append('        #and classification is described here:')

    lines.append('        org = Organization(name="org_name", classification="legislature")')
    lines.append('')

    lines.append('        #OPTIONAL: add posts to your organizaion using thi format,')
    lines.append('        #where label is a human-readable description of the post (eg "Ward 8 conucilmember")')
    lines.append('        #and role is the positoin type (eg conucilmember, alderman, mayor...)')
    lines.append('        #skip entirely if you\'re not writing a people scraper.')
    lines.append('        org.add_post(label="position_description", role="position_type")')
    lines.append('')
    lines.append('        #REQUIIRED: yield the organization')
    lines.append('        yield org')
    lines.append('')

    with open(os.path.join(dirname, '__init__.py'), 'w') as of:
        of.write('\n'.join(lines))

    # write scraper files
    for stype in scraper_types:
        lines = ['from pupa.scrape import Scraper']
        lines.append('from pupa.scrape import {}'.format(CLASS_DICT[stype]))
        lines.append('')
        lines.append('')
        lines.append('class {}{}Scraper(Scraper):'.format(camel_case, CLASS_DICT[stype]))
        lines.append('')
        lines.append('    def scrape(self):')
        lines.append('        # needs to be implemented')
        lines.append('        pass')
        lines.append('')
        with open(os.path.join(dirname, stype + '.py'), 'w') as of:
            of.write('\n'.join(lines))


class Command(BaseCommand):
    name = 'init'
    help = 'start a new pupa scraper'

    def add_args(self):
        self.add_argument('module', type=str, help='name of the new scraper module')

    def handle(self, args, other):

        name = prompt('jurisdiction name (e.g. City of Seattle): ')
        division = prompt('division id (look this up in the opencivicdata/ocd-division-ids repository): ')
        classification = prompt('classification (can be: {}): '
                                .format(', '.join(JURISDICTION_CLASSIFICATIONS)))
        url = prompt('official URL: ')

        try:
            Division.get(division)
        except ValueError:
            print("\nERROR: Division ID is invalid.",\
                    "Please find the correct division_id here",\
                    "https://github.com/opencivicdata/ocd-division-ids/tree/master/identifiers",\
                    "or contact open-civic-data@googlegroups.org to add a new country\n")
            sys.exit(1)

        if os.path.exists(args.module):
            raise CommandError(args.module + ' directory already exists')
        os.makedirs(args.module)

        # will default to True until they pick one, then defaults to False
        scraper_types = CLASS_DICT.keys()
        selected_scraper_types = []
        for stype in scraper_types:
            prompt_str = 'create {} scraper? {}: '.format(
                stype, '[y/N]' if selected_scraper_types else '[Y/n]')
            default = 'N' if selected_scraper_types else 'Y'
            result = prompt(prompt_str, default).upper()
            if result == 'Y':
                selected_scraper_types.append(stype)

        write_jurisdiction_template(args.module, args.module, name, division, classification, url,
                                    selected_scraper_types)
