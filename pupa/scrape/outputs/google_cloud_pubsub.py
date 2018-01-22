import os
import json
from collections import OrderedDict

from pupa import utils
from pupa.scrape.outputs.output import Output

from google.cloud import pubsub


class GoogleCloudPubSub(Output):

    def __init__(self, scraper):
        super().__init__(scraper)

        self.project = os.environ.get('GOOGLE_CLOUD_PROJECT')
        self.topic_name = os.environ.get('GOOGLE_CLOUD_PUBSUB_TOPIC')

    def handle_output(self, obj):
        publisher = pubsub.PublisherClient()
        topic_path = publisher.topic_path(self.project, self.topic_name)

        self.scraper.info('save %s %s to topic %s', obj._type, obj, topic_path)
        self.scraper.debug(json.dumps(OrderedDict(sorted(obj.as_dict().items())),
                           cls=utils.JSONEncoderPlus,
                           indent=4, separators=(',', ': ')))

        self.add_output_name(obj, topic_path)
        obj_str = self.stringify_obj(obj, True, True)

        publisher.publish(topic_path, obj_str.encode('utf-8'))
