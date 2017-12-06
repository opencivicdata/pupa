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

        info = {
            'type': 'service_account',
            'project_id': project_id,
            'private_key_id': os.environ.get(
                'GOOGLE_CLOUD_PUBSUB_PRIVATE_KEY_ID',
                ''),
            'private_key': os.environ.get(
                'GOOGLE_CLOUD_PUBSUB_PRIVATE_KEY',
                ''),
            'client_email': os.environ.get(
                'GOOGLE_CLOUD_PUBSUB_CLIENT_EMAIL',
                ''),
            'client_id': os.environ.get('GOOGLE_CLOUD_PUBSUB_CLIENT_ID', ''),
            'auth_uri': os.environ.get(
                'GOOGLE_CLOUD_PUBSUB_AUTH_URI',
                'https://accounts.google.com/o/oauth2/auth'),
            'token_uri': os.environ.get(
                'GOOGLE_CLOUD_PUBSUB_TOKEN_URI',
                'https://accounts.google.com/o/oauth2/token'),
            'auth_provider_x509_cert_url': os.environ.get(
                'GOOGLE_CLOUD_PUBSUB_AUTH_CERT_URL',
                'https://www.googleapis.com/oauth2/v1/certs'),
            'client_x509_cert_url': os.environ.get(
                'GOOGLE_CLOUD_PUBSUB_CLIENT_CERT_URL',
                ''),
        }

        # TODO: Remove!
        self.caller.info(json.dumps(info))

        credentials = service_account.Credentials.from_service_account_info(info)

        self.publisher = pubsub.PublisherClient(credentials=credentials)

        self.topic = 'projects/{project_id}/topics/{topic}'.format(
                    project_id=project_id,
                    topic=topic)

        self.caller = caller

        try:
            self.publisher.create_topic(self.topic) # raises conflict if topic exists
        except Exception:
            pass

    def save_object(self, obj):
        obj.pre_save(self.caller.jurisdiction.jurisdiction_id)

        self.caller.info('save %s %s to topic %s', obj._type, obj, self.topic)
        self.caller.debug(json.dumps(OrderedDict(sorted(obj.as_dict().items())),
                                     cls=utils.JSONEncoderPlus,
                                     indent=4, separators=(',', ': ')))

        self.caller.output_names[obj._type].add(obj)

        # Copy the original object so we can tack on jurisdiction and type
        output_obj = obj.as_dict()

        if self.caller.jurisdiction:
            output_obj['jurisdiction'] = self.caller.jurisdiction.jurisdiction_id

        output_obj['type'] = obj._type

        output_obj = OrderedDict(sorted(output_obj.items()))

        # TODO: Should add a messagepack CLI option
        message = json.dumps(output_obj, cls=utils.JSONEncoderPlus).encode()

        self.publisher.publish(
            self.topic,
            message,
            pubdate=datetime.now(timezone.utc).strftime('%c'))

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
