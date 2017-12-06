import os
import json
from collections import OrderedDict
from datetime import datetime, timezone

from pupa import utils

from google.oauth2 import service_account
from google.cloud import pubsub


class GoogleCloudPubSub():

    def __init__(self, caller):
        project_id = os.environ.get('GOOGLE_CLOUD_PUBSUB_PROJECT_ID', '')
        topic = os.environ.get('GOOGLE_CLOUD_PUBSUB_TOPIC', '')
        info = json.loads(os.environ.get('GOOGLE_CLOUD_PUBSUB_CREDENTIALS'))
        print(info)
    #     scope = 'https://www.googleapis.com/auth/pubsub'
    #
    #     credentials = service_account.Credentials.from_service_account_info(
    #         info,
    #         scopes=(scope,))
    #
    #     self.publisher = pubsub.PublisherClient(credentials=credentials)
    #
    #     self.topic = 'projects/{project_id}/topics/{topic}'.format(
    #                 project_id=project_id,
    #                 topic=topic)
    #
    #     self.caller = caller
    #
    #     try:
    #         # raises conflict if topic exists
    #         self.publisher.create_topic(self.topic)
    #     except Exception:
    #         pass
    #
    # def save_object(self, obj):
    #     obj.pre_save(self.caller.jurisdiction.jurisdiction_id)
    #
    #     self.caller.info('save %s %s to topic %s', obj._type, obj, self.topic)
    #     self.caller.debug(json.dumps(OrderedDict(sorted(obj.as_dict().items())),
    #                                  cls=utils.JSONEncoderPlus,
    #                                  indent=4, separators=(',', ': ')))
    #
    #     self.caller.output_names[obj._type].add(obj)
    #
    #     # Copy the original object so we can tack on jurisdiction and type
    #     output_obj = obj.as_dict()
    #
    #     if self.caller.jurisdiction:
    #         output_obj['jurisdiction'] = self.caller.jurisdiction.jurisdiction_id
    #
    #     output_obj['type'] = obj._type
    #
    #     output_obj = OrderedDict(sorted(output_obj.items()))
    #
    #     # TODO: Should add a messagepack CLI option
    #     message = json.dumps(output_obj, cls=utils.JSONEncoderPlus).encode()
    #
    #     self.publisher.publish(
    #         self.topic,
    #         message,
    #         pubdate=datetime.now(timezone.utc).strftime('%c'))
    #
    #     # validate after writing, allows for inspection on failure
    #     try:
    #         # Note we're validating the original object, not the output object,
    #         # Because we add some relevant-to-us but out of schema metadata to the output object
    #         obj.validate()
    #     except Exception as ve:
    #         if self.caller.strict_validation:
    #             raise ve
    #         else:
    #             self.caller.warning(ve)
    #
    #     # after saving and validating, save subordinate objects
    #     for obj in obj._related:
    #         self.save_object(obj)
