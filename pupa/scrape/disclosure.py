from .base import BaseModel, SourceMixin, AssociatedLinkMixin, IdentifierMixin
from .schemas.disclosure import disclosure_schema, reporting_period_schema


class DisclosureReportingPeriod(BaseModel):

    _type = 'reporting-period'
    _schema = reporting_period_schema

    def __init__(self, name, start_time, end_time, period_type, description):
        self.name = name
        self.start_date = start_time
        self.end_date = end_time
        self.period_type = period_type
        self.authorities = []

    def add_authority(self, name, type, *, jurisdiction=None, id=None):
        self.authorities.append({
            "name": name,
            "id": id,
            "jurisdiction": jurisdiction,
            "type": type,
        })


class Disclosure(BaseModel, SourceMixin, AssociatedLinkMixin, IdentifierMixin):
    """
    Details for a Disclosure in .format
    """
    _type = 'disclosure'
    _schema = disclosure_schema

    def __init__(self, effective_date, timezone, submitted_date=None,
                 classification=None):
        super(Disclosure, self).__init__()
        self.classification = classification
        self.effective_date = effective_date
        self.timezone = timezone
        self.submitted_date = submitted_date
        self.related_entities = []
        self.disclosed_events = []
        self.identifiers = []
        self.documents = []
        self.extras = {}

    def add_registrant(self, name, type, *, classification=None, id=None, note='registrant'):
        self.add_entity(name=name,
                        entity_type=type,
                        classification=classification,
                        note='registrant',
                        id=id)

    def add_authority(self, name, type, *, classification=None, id=None,
                      note='authority'):
        self.add_entity(name=name,
                        entity_type=type,
                        classification=classification,
                        note=note,
                        id=id)

    # TODO: may want to avoid making an id, here
    # def add_reporting_period(self, name, type, *, id=None, note="reporting_period"):
    #     self.add_entity(name=name,
    #                     entity_type=type,
    #                     id=id,
    #                     note=note)

    def add_document(self, note, url, *, media_type='', on_duplicate='error',
                     date=''):
        return self._add_associated_link(collection='documents',
                                         note=note,
                                         url=url,
                                         media_type=media_type,
                                         on_duplicate=on_duplicate,
                                         date=date)

    def add_disclosed_event(self, disclosed_event):
        self.disclosed_events.append({
            "name": disclosed_event.name,
            "entity_type": disclosed_event._type,
            "id": disclosed_event._id,
        })
        self._related.append(disclosed_event)

    def add_entity(self, name, entity_type, *, classification=None, id=None, note):
        ret = {
            "name": name,
            "entity_type": entity_type,
            "note": note
        }
        if id:
            ret['id'] = id
        if classification:
            ret['classification'] = classification
        self.related_entities.append(ret)
