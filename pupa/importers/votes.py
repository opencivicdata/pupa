from .base import BaseImporter


class VoteImporter(BaseImporter):
    _type = 'vote'

    def prepare_object_from_json(self, obj):
        return obj
