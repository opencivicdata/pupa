from opencivicdata.core.models import Jurisdiction
from opencivicdata.legislative.models import LegislativeSession
from .base import BaseImporter


class JurisdictionImporter(BaseImporter):
    _type = 'jurisdiction'
    model_class = Jurisdiction
    related_models = {'legislative_sessions': (LegislativeSession, 'jurisdiction_id', {})}
    merge_related = {'legislative_sessions': ['identifier']}

    def get_object(self, data):
        return self.model_class.objects.get(division_id=data['division_id'],
                                            classification=data['classification'])

    def prepare_for_db(self, data):
        for s in data['legislative_sessions']:
            s.pop('_scraped_name', None)
        return data
