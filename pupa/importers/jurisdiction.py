from opencivicdata.models import Jurisdiction, JurisdictionSession
from .base import BaseImporter


class JurisdictionImporter(BaseImporter):
    _type = 'jurisdiction'
    model_class = Jurisdiction
    related_models = {'sessions': JurisdictionSession}

    def __init__(self, jurisdiction_id):
        super(JurisdictionImporter, self).__init__(jurisdiction_id)

    def prepare_for_db(self, data):
        data.pop('building_maps')   # TODO: drop this if we start importing building_maps
        return data

    def get_object(self, data):
        return self.model_class.objects.get(id=data['id'])
