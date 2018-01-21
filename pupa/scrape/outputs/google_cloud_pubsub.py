import os
import json
from collections import OrderedDict
from datetime import datetime, timezone

from pupa import utils
from pupa.scrape.outputs.output import Output

from google.cloud import pubsub


class GoogleCloudPubSub(Output):

    def __init__(self, scraper):
        super().__init__(scraper)

        self.publisher = pubsub.PublisherClient()
        self.topic_path = self.publisher.topic_path(
            os.environ.get('GOOGLE_CLOUD_PROJECT'),
            os.environ.get('GOOGLE_CLOUD_PUBSUB_TOPIC'))

    def handle_output(self, obj):
        self.scraper.info('save %s %s to topic %s', obj._type, obj, self.topic_path)
        self.scraper.debug(json.dumps(OrderedDict(sorted(obj.as_dict().items())),
                           cls=utils.JSONEncoderPlus,
                           indent=4, separators=(',', ': ')))

        self.scraper.output_names[obj._type].add(obj)

        # Copy the original object so we can tack on jurisdiction and type
        output_obj = obj.as_dict()

        if self.scraper.jurisdiction:
            output_obj['jurisdiction'] = self.scraper.jurisdiction.jurisdiction_id

        output_obj['type'] = obj._type

        # TODO: Should add a messagepack CLI option
        message = json.dumps(output_obj,
                             cls=utils.JSONEncoderPlus,
                             separators=(',', ':')).encode('utf-8')

        self.publisher.publish(
            self.topic_path,
            message,
            pubdate=datetime.now(timezone.utc).strftime('%c'))
