import json
import os
from collections import OrderedDict

from pupa import utils
from pupa.scrape.outputs.output import Output


class LocalFile(Output):

    def handle_output(self, obj):
        filename = '{0}_{1}.json'.format(obj._type, obj._id).replace('/', '-')

        self.scraper.info('save %s %s as %s', obj._type, obj, filename)
        self.scraper.debug(json.dumps(OrderedDict(sorted(obj.as_dict().items())),
                           cls=utils.JSONEncoderPlus, indent=4, separators=(',', ': ')))

        self.scraper.output_names[obj._type].add(filename)

        with open(os.path.join(self.scraper.datadir, filename), 'w') as f:
            json.dump(obj.as_dict(), f, cls=utils.JSONEncoderPlus)
