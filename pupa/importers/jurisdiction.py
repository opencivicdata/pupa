from opencivicdata.models import Jurisdiction, LegislativeSession
from .base import BaseImporter


class JurisdictionImporter(BaseImporter):
    _type = 'jurisdiction'
    model_class = Jurisdiction
    related_models = {'legislative_sessions': (LegislativeSession, 'jurisdiction_id', {})}
    merge_related = {'legislative_sessions': ['identifier']}

    def get_object(self, data):
        return self.model_class.objects.get(division_id=data['division_id'],
                                            classification=data['classification'])
