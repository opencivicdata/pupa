from pupa.models import Jurisdiction
from .base import BaseImporter


class JurisdictionImporter(BaseImporter):
    _type = 'jurisdiction'
    _model_class = Jurisdiction

    def __init__(self, jurisdiction_id):
        super(JurisdictionImporter, self).__init__(jurisdiction_id)

    def get_db_spec(self, jurisdiction):
        return {'_id': jurisdiction.jurisdiction_id}
