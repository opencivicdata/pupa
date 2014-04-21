from pupa.models.jurisdiction import Jurisdiction, JurisdictionSession
from .base import BaseImporter


class JurisdictionImporter(BaseImporter):
    _type = 'jurisdiction'
    model_class = Jurisdiction
    related_models = {'sessions': JurisdictionSession}

    def __init__(self, jurisdiction_id):
        super(JurisdictionImporter, self).__init__(jurisdiction_id)

    def get_object(self, data):
        return self.model_class.objects.get(id=data['id'])
