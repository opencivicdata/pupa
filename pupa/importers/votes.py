from .base import BaseImporter


class VoteImporter(BaseImporter):
    _type = 'vote'

    def get_db_spec(self, event):
        spec = {
            "motion": event['motion'],
            "chamber": event['chamber'],
            "date": event['date'],
        }
        return spec

    def prepare_object_from_json(self, obj):
        return obj
