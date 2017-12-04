import os
import json
import uuid
import logging
from collections import defaultdict, OrderedDict
from datetime import datetime, timezone

import scrapelib

from pupa import utils
from pupa import settings

from pupa.scrape import Scraper, Bill, VoteEvent

from pupa.exceptions import ScrapeError, ScrapeValueError

from google.cloud import pubsub

# export GOOGLE_APPLICATION_CREDENTIALS=<path_to_service_account_file>
# export GOOGLE_CLOUD_PROJECT=<project id>
# export GOOGLE_CLOUD_TOPIC=<topic>

class GcpsScraper():

    def __init__(self, caller):

        self.publisher = pubsub.PublisherClient()

        self.topic = 'projects/{project_id}/topics/{topic}'.format(
                    project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
                    topic=os.getenv('GOOGLE_CLOUD_TOPIC'),
                )

        self.caller = caller

        try:
            self.publisher.create_topic(self.topic)  # raises conflict if topic exists
        except Exception:
            pass

    def save_object(self, obj):

        self.caller.info('save %s %s to topic %s', obj._type, obj, self.topic)
        self.caller.debug(json.dumps(OrderedDict(sorted(obj.as_dict().items())),
                                cls=utils.JSONEncoderPlus, indent=4, separators=(',', ': ')))

        self.caller.output_names[obj._type].add(obj)

        # Copy the original object so we can tack on jurisdiction and type
        output_obj = obj.as_dict()

        if self.caller.jurisdiction:
            output_obj['jurisdiction'] = self.caller.jurisdiction.jurisdiction_id

        output_obj['type'] = obj._type

        output_obj = OrderedDict(sorted(output_obj.items()))

        # TODO: Should add a messagepack CLI option
        message = json.dumps(output_obj, cls=utils.JSONEncoderPlus).encode()

        self.publisher.publish(self.topic, message, pubdate=datetime.now(timezone.utc).strftime("%c"))

        # validate after writing, allows for inspection on failure
        try:
            # Note we're validating the original object, not the output object,
            # Because we add some relevant-to-us but out of schema metadata to the output object
            obj.validate()
        except Exception as ve:
            self.warning(ve)
            if self.strict_validation:
                raise ve

        # after saving and validating, save subordinate objects
        for obj in obj._related:
            self.save_object(obj)
