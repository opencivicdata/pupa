import os
import json
import uuid
import logging
from collections import defaultdict, OrderedDict

import scrapelib
from validictory import ValidationError

from pupa import utils
from pupa import settings
from pupa import scrape

from pupa.scrape import Scraper, Bill, VoteEvent

from kafka import KafkaProducer
from kafka.errors import KafkaError

from pupa.exceptions import ScrapeError, ScrapeValueError

class KafkaScraper(Scraper):

    def __init__(self):
        self.kafka_servers = []
        for server in settings.KAFKA_SERVERS.split():
            self.kafka_servers.append(server)
        #super(KafkaScraper, self).__init__()

        self.producer = KafkaProducer(bootstrap_servers=self.kafka_servers)

    def save_object(self, obj):

        self.info('save %s %s to topic %s', obj._type, obj, settings.KAFKA_TOPIC)
        # self.debug(json.dumps(OrderedDict(sorted(obj.as_dict().items())),
        #                         cls=utils.JSONEncoderPlus, indent=4, separators=(',', ': ')))

        self.output_names[obj._type].add(obj)

        # Copy the original object so we can tack on jurisdiction and type
        kafka_obj = obj.as_dict()

        if self.jurisdiction:
            kafka_obj['jurisdiction'] = self.jurisdiction.jurisdiction_id

        kafka_obj['type'] = obj._type

        kafka_obj = OrderedDict(sorted(kafka_obj.items()))

        # TODO: Should probably add a messagepack CLI option
        message = json.dumps(kafka_obj, cls=utils.JSONEncoderPlus).encode()
        self.send_kafka(settings.KAFKA_TOPIC, message)

        # validate after writing, allows for inspection on failure
        try:
            # Note we're validating the original object, not the kafka object,
            # Because we add some relevant-to-kafka but out of schema metadata to the kafka object
            obj.validate()
        except KafkaError as ve:
            self.warning(ve)
            if self.strict_validation:
                raise ve

        # after saving and validating, save subordinate objects
        for obj in obj._related:
            self.save_object(obj)

    def send_kafka(self, topic, message):
        try:
            self.producer.send(topic, message)
        except KafkaError as ke:
            self.warning(ke)
            if self.strict_validation:
                raise ke
