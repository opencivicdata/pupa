from .base import BaseModel, SourceMixin, AssociatedLinkMixin, LinkMixin
from .schemas.disclosure import disclosure_schema, reporting_period_schema


class DisclosureReportingPeriod(BaseModel):

    _type = 'disclosure-reporting-period'
    _schema = reporting_period_schema

    def __init__(self, name, start_time, end_time, period_type):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.period_type = period_type
    
    def add_authority(self, name, id):
        self.authority = name
        self.authority_id = id


class Disclosure(BaseModel, SourceMixin, AssociatedLinkMixin):
    """
    Details for a Disclosure in .format
    """
    _type = 'disclosure'
    _schema = schema

    def __init__(self, disclosure_id, effective_date):
        super(Disclosure, self).__init__()
        self._id = disclosure_id
        self.effective_date = effective_date
        self.registrant = ""
        self.registrant_id = ""
        self.authority = ""
        self.authority_id = ""
        self.reporting_period = None
        self.related_entities = []
        self.identifiers = []
        self.created_at = datetime.now.isoformat()
        self.updated_at = None
        self.documents = []
        self.disclosed_events = []
        self.extras = {}

    def add_registrant(self, registrant):
        self._related.append(registrant)
        self.add_entity(name=registrant['name'],
                        entity_type=registrant._type,
                        id=registrant['id'],
                        note='registrant')
        self.registrant = registrant.name
        self.registrant_id = registrant._id
        pass

    def add_authority(self, authority):
        self.add_entity(name=registrant['name'],
                        entity_type=registrant._type,
                        id=registrant['id'],
                        note='authority')
        self.authority = authority.name
        self.authority_id = authority._id

    def add_document(self, note, url, *, media_type='', on_duplicate='error'):
        return self._add_associated_link(collection='documents',
                                         note=note,
                                         url=url,
                                         *,
                                         media_type=media_type,
                                         on_duplicate=on_duplicate)

    def add_disclosed_event(self, disclosed_event):
        self.disclosed_events.append(disclosed_event)
        self._related.append(disclosed_event)

    def add_entity(self, name, entity_type, *, id, note):
        ret = {
            "name": name,
            "entity_type": entity_type,
            "note": note
        }
        if id:
            ret['id'] = id
        self['related_entities'].append(ret)
