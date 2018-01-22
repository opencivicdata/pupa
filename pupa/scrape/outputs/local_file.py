import json
import os

from pupa import utils
from pupa.scrape.outputs.output import Output


class LocalFile(Output):

    def handle_output(self, obj):
        filename = '{0}_{1}.json'.format(obj._type, obj._id).replace('/', '-')

        self.scraper.info('save %s %s as %s', obj._type, obj, filename)
        self.debug_obj(obj)

        self.add_output_name(obj, filename)

        with open(os.path.join(self.scraper.datadir, filename), 'w') as f:
            json.dump(obj.as_dict(), f, cls=utils.JSONEncoderPlus)
