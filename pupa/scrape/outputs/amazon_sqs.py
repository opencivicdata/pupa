import boto3
import os
import json
from collections import OrderedDict

from pupa import utils
from pupa.scrape.outputs.output import Output


class AmazonSQS(Output):

    def __init__(self, scraper):
        super().__init__(scraper)

        self.sqs = boto3.resource('sqs')
        self.queue_name = os.environ.get('AMAZON_SQS_QUEUE')
        self.queue = self.sqs.get_queue_by_name(QueueName=self.queue_name)

    def handle_output(self, obj):
        self.scraper.info('save %s %s to queue %s', obj._type, obj, self.queue_name)
        self.scraper.debug(json.dumps(OrderedDict(sorted(obj.as_dict().items())),
                           cls=utils.JSONEncoderPlus,
                           indent=4, separators=(',', ': ')))

        self.scraper.output_names[obj._type].add(obj)

        # Copy the original object so we can tack on jurisdiction and type
        output_obj = obj.as_dict()

        if self.scraper.jurisdiction:
            output_obj['jurisdiction'] = self.scraper.jurisdiction.jurisdiction_id

        output_obj['type'] = obj._type

        message = json.dumps(output_obj,
                             cls=utils.JSONEncoderPlus,
                             separators=(',', ':')).encode('utf-8')

        self.queue.send_message(MessageBody=message)
