import sys
from os.path import join, abspath, dirname

import sh
import lxml.html
from libmproxy import proxy, flow

from pupa.scrape import Scraper
from pupa.models import Bill


class LegistarScraper(Scraper):
    '''
    Record yourself exporting the excel spreadsheet using mitmproxy.
    Save the mitm flows to a file called 'mitmdump.in' in the scraper folder.
    Good to go.

    Then subclass this like so:

    class BillScraper(LegstarScraper):
        url = 'https://chicago.legistar.com/Legislation.aspx'
        columns = (
                'bill_id', 'enactment_id', 'type', 'status',
                'created', 'action', 'title')

    Where columns are the columns from the excel sheet.
    '''

    def get_bill_ids(self):
        filename = sys.modules[self.__class__.__module__].__file__
        here = dirname(abspath(filename))
        infile = join(here, 'mitmdump.in')
        outfile = join(here, 'mitmdump.out')

        if self.requests_per_minute:
            sh.mitmdump(
                n=True,       # Don't start proxy server.
                c=infile,     # Client replay of saved flows.
                w=outfile)    # Output file.

        with open(outfile) as f:
            flows = list(flow.FlowReader(f).stream())
        workbook = flows[-1].response.content.decode('utf-8')

        doc = lxml.html.fromstring(workbook)

        for tr in doc.xpath('//tr')[1:]:
            vals = [td.text_content() for td in tr.xpath('td')]
            vals = [val.strip().replace(u'\xa0', '') for val in vals]
            keys = self.columns
            data = dict(zip(keys, vals))

            if not data['title']:
                continue
            _type = self.get_type(data.get('type').lower())
            if _type not in ['ordinance', 'resolution']:
                continue
            else:
                data['type'] = _type

            yield data.pop('bill_id'), data

    def get_type(self, _type):
        return _type

    def get_bill(self, bill_id, **kwargs):
        title = kwargs.pop('title')
        _type = kwargs.pop('type')
        bill = Bill(bill_id, self.session, title=title, type=_type)
        bill.add_source(self.url)
        return bill
