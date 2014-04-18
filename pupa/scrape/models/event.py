from .base import BaseModel, SourceMixin, AssociatedLinkMixin, LinkMixin
from .schemas.event import schema


class EventAgendaItem(dict, AssociatedLinkMixin):
    event = None

    def __init__(self, description, event):
        super(EventAgendaItem, self).__init__({
            "description": description,
            "related_entities": [],
            "subjects": [],
            "media": [],
            "notes": [],
            "order": None,
        })
        self.event = event

    def add_subject(self, what):
        self['subjects'].append(what)

    def add_committee(self, committee, id=None, note='participant'):
        self.add_entity(name=committee, type='committee', id=id, note=note)

    def add_bill(self, bill, id=None, note='consideration'):
        self.add_entity(name=bill, type='bill', id=id, note=note)

    def add_person(self, person, id=None, note='participant'):
        self.add_entity(name=person, type='person', id=id, note=note)

    def add_media_link(self, name, url, type='media', mimetype=None, offset=None,
                       on_duplicate='error'):
        return self._add_associated_link(collection='media', name=name, url=url, type=type,
                                         offset=offset, mimetype=mimetype,
                                         on_duplicate=on_duplicate)

    def add_entity(self, name, type, id, note):
        self['related_entities'].append({"name": name, "type": type, "id": id, "note": note})


class Event(BaseModel, SourceMixin, AssociatedLinkMixin, LinkMixin):
    """
    Details for an event in .format
    """
    _type = 'event'
    _schema = schema
    _collection = 'events'

    def __init__(self, name, when, location, **kwargs):
        super(Event, self).__init__()
        self.when = when
        self.name = name
        self.all_day = False
        self.documents = []
        self.description = None
        self.end = None
        self.location = {"name": location, "note": None, "coordinates": None}
        self.participants = []
        self.media = []
        self.agenda = []
        self.sources = []
        self.status = "confirmed"
        self.type = "event"
        self._related = []

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return u'{0} {1}'.format(self.when, self.name.strip())
    __unicode__ = __str__

    def add_participant(self, name, type, note='participant', chamber=None, id=None):
        self.participants.append({"chamber": chamber, "type": type, "note": note, "name": name,
                                  "id": id})

    def add_person(self, name, note='participant', chamber=None, id=None):
        return self.add_participant(name=name, type='person', chamber=chamber, note=note)

    def add_agenda_item(self, description):
        obj = EventAgendaItem(description, self)
        self.agenda.append(obj)
        return obj

    def add_media_link(self, name, url, type='media', mimetype=None, offset=None,
                       on_duplicate='error'):
        return self._add_associated_link(collection='media', name=name, url=url, type=type,
                                         offset=offset, mimetype=mimetype,
                                         on_duplicate=on_duplicate)

    def add_document(self, name, url, mimetype=None, on_duplicate='error'):
        return self._add_associated_link(collection='documents', name=name, url=url,
                                         type='document', mimetype=mimetype,
                                         on_duplicate=on_duplicate)
