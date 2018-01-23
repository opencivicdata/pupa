import os

from pupa.scrape.outputs.output import Output

from google.cloud import pubsub


class GoogleCloudPubSub(Output):

    def __init__(self, scraper):
        super().__init__(scraper)

        project = os.environ.get('GOOGLE_CLOUD_PROJECT')
        topic_name = os.environ.get('GOOGLE_CLOUD_PUBSUB_TOPIC')
        self.publisher = pubsub.PublisherClient()
        self.topic_path = self.publisher.topic_path(project, topic_name)

    def handle_output(self, obj):
        self.scraper.info('publish %s %s to topic %s', obj._type, obj,
                          self.topic_path)
        self.debug_obj(obj)

        self.add_output_name(obj, self.topic_path)
        obj_str = self.stringify_obj(obj, True, True)

        self.publisher.publish(self.topic_path, obj_str.encode('utf-8'))
