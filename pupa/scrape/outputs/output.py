from abc import ABCMeta, abstractmethod


class Output(metaclass=ABCMeta):

    def __init__(self, scraper):
        self.scraper = scraper

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
