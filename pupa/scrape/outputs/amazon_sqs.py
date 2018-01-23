import boto3
import os
import json
import uuid
from collections import OrderedDict

from pupa import utils
from pupa.scrape.outputs.output import Output

MAX_BYTE_LENGTH = 230_000


class AmazonSQS(Output):

    def __init__(self, scraper):
        super().__init__(scraper)

        self.sqs = boto3.resource('sqs')
        self.queue_name = os.environ.get('AMAZON_SQS_QUEUE')
        self.queue = self.sqs.get_queue_by_name(QueueName=self.queue_name)

        self.s3 = boto3.resource('s3')
        self.bucket_name = os.environ.get('AMAZON_S3_BUCKET')

    def handle_output(self, obj):
        self.scraper.info('send %s %s to queue %s', obj._type, obj,
                          self.queue_name)
        self.debug_obj(obj)

        self.add_output_name(obj, self.queue_name)
        obj_str = self.stringify_obj(obj, True, True)
        encoded_obj_str = obj_str.encode('utf-8')

        if len(encoded_obj_str) > MAX_BYTE_LENGTH:
            key = 'S3:{}'.format(str(uuid.uuid4()))

            self.scraper.info('put %s %s to bucket %s/%s', obj._type, obj,
                              self.bucket_name, key)

            self.s3.Object(self.bucket_name, key).put(Body=encoded_obj_str)
            self.queue.send_message(MessageBody=key)
        else:
            self.queue.send_message(MessageBody=obj_str)
