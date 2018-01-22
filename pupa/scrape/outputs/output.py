import json

from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from datetime import datetime, timezone

from pupa import utils


class Output(metaclass=ABCMeta):

    def __init__(self, scraper):
        self.scraper = scraper

    def add_output_name(self, obj, output_name):
        self.scraper.output_names[obj._type].add(output_name)

    def debug_obj(self, obj):
        self.scraper.debug(json.dumps(OrderedDict(sorted(obj.as_dict().items())),
                           cls=utils.JSONEncoderPlus,
                           indent=4, separators=(',', ': ')))

    def get_obj_as_dict(self, obj, add_jurisdiction=False, add_type=False):
        obj_dict = obj.as_dict()
        if add_jurisdiction and self.scraper.jurisdiction:
            obj_dict['jurisdiction'] = self.scraper.jurisdiction.jurisdiction_id
        if add_type:
            obj_dict['type'] = obj._type
        return obj_dict

    @abstractmethod
    def handle_output(self, obj):
        pass

    def save_object(self, obj):
        obj.pre_save(self.scraper.jurisdiction.jurisdiction_id)

        # actual output handling, to be handled by subclass
        self.handle_output(obj)

        # validate after writing, allows for inspection on failure
        try:
            obj.validate()
        except ValueError as ve:
            if self.scraper.strict_validation:
                raise ve
            else:
                self.scraper.warning(ve)

        # after saving and validating, save subordinate objects
        for obj in obj._related:
            self.save_object(obj)

    def stringify_obj(self, obj, add_jurisdiction=False, add_type=False):
        obj_dict = self.get_obj_as_dict(obj, add_jurisdiction, add_type)
        return self.stringify_obj_dict(obj_dict)

    def stringify_obj_dict(self, obj_dict):
        return json.dumps(obj_dict, cls=utils.JSONEncoderPlus,
                          separators=(',', ':'))
