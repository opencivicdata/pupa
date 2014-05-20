from opencivicdata.models import Jurisdiction
from .base import BaseImporter


class JurisdictionImporter(BaseImporter):
    _type = 'jurisdiction'
    model_class = Jurisdiction
    related_models = {'sessions': {}}

    def get_object(self, data):
        return self.model_class.objects.get(id=data['id'])
