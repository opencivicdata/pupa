import os
import json

from pupa.models.statutes import StructureNode, ContentNode, Edge
from pupa.utils import JSONEncoderPlus
from pupa.utils.urls import Urls
from .base import Scraper


class StatuteScraper(Scraper):

    def __init__(self, *args, **kwargs):
        super(StatuteScraper, self).__init__(*args, **kwargs)
        self.urls = Urls(self)

    def get_statutes(self):
        msg = '%s must provide a get_statutes() method.'
        raise NotImplementedError(msg % self.__class__.__name__)

    def scrape_statutes(self):
        return self._scrape(self.get_statutes(), 'statutes')

    def add_node(self, node):
        filename = '{0}_{1}.json'.format(node._type, node._id)
        self.info('save %s %s as %s', node._type, node, filename)
        self.output_names[node._type].add(filename)
        with open(os.path.join(self.output_dir, filename), 'w') as f:
            json.dump(node.as_dict(), f, cls=JSONEncoderPlus)

        # validate after writing, allows for inspection on failure
        try:
            node.validate()
        except ValueError as ve:
            self.warning(ve)
            if self.strict_validation:
                raise ve

    def add_edge(self, node1, node2):
        '''Passed in nodes can be uuid's or StructureNode
        instances.
        '''
        edge = Edge(node1, node2)
        filename = '{0}_{1}.json'.format(edge._type, edge._id)
        self.info('save %s %s as %s', edge._type, edge, filename)
        self.output_names[edge._type].add(filename)
        with open(os.path.join(self.output_dir, filename), 'w') as f:
            json.dump(edge.as_dict(), f, cls=JSONEncoderPlus)

        # validate after writing, allows for inspection on failure
        try:
            edge.validate()
        except ValueError as ve:
            self.warning(ve)
            if self.strict_validation:
                raise ve
