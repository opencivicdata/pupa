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
        self.scraper.info('send %s %s to queue %s', obj._type, obj,
                          self.queue_name)
        self.debug_obj(obj)

        self.add_output_name(obj, self.queue_name)
        obj_str = self.stringify_obj(obj, True, True)

        self.queue.send_message(MessageBody=obj_str)
