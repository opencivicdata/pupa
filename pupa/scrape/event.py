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
            "order": str(len(event.agenda)),
        })
        self.event = event

    def add_subject(self, what):
        self['subjects'].append(what)

    def add_vote(self, vote, *, id=None, note='consideration'):
        self.add_entity(name=vote, entity_type='vote', id=id, note=note)

    def add_committee(self, committee, *, id=None, note='participant'):
        self.add_entity(name=committee, entity_type='committee', id=id, note=note)

    def add_bill(self, bill, *, id=None, note='consideration'):
        self.add_entity(name=bill, entity_type='bill', id=id, note=note)

    def add_person(self, person, *, id=None, note='participant'):
        self.add_entity(name=person, entity_type='person', id=id, note=note)

    def add_media_link(self, note, url, media_type, *, type='media', on_duplicate='error'):
        return self._add_associated_link(collection='media', note=note, url=url,
                                         media_type=media_type, on_duplicate=on_duplicate)

    def add_entity(self, name, entity_type, *, id, note):
        ret = {
            "name": name,
            "entity_type": entity_type,
            "note": note
        }
        if id:
            ret['id'] = id
        self['related_entities'].append(ret)


class Event(BaseModel, SourceMixin, AssociatedLinkMixin, LinkMixin):
    """
    Details for an event in .format
    """
    _type = 'event'
    _schema = schema

    def __init__(self, name, start_time, timezone, location_name, *,
                 all_day=False, description="", end_time=None,
                 status="confirmed", classification="event"):
        super(Event, self).__init__()
        self.start_time = start_time
        self.timezone = timezone
        self.all_day = all_day
        self.end_time = end_time
        self.name = name
        self.description = description
        self.status = status
        self.classification = classification
        self.location = {"name": location_name, "note": "", "coordinates": None}
        self.documents = []
        self.participants = []
        self.media = []
        self.agenda = []

    def __str__(self):
        return '{} {}'.format(self.start_time, self.name.strip())

    def set_location(self, name, *, note="", coordinates=None):
        self.location = {"name": name, "note": note, "coordinates": coordinates}

    def add_participant(self, name, type, *, id=None, note='participant'):
        p = {
            "name": name,
            "entity_type": type,
            "note": note
        }
        if id:
            p['id'] = id
        self.participants.append(p)

    def add_person(self, name, *, id=None, note='participant'):
        return self.add_participant(name=name, type='person', id=id, note=note)

    def add_committee(self, name, *, id=None, note='participant'):
        return self.add_participant(name=name, type='organization', id=id, note=note)

    def add_agenda_item(self, description):
        obj = EventAgendaItem(description, self)
        self.agenda.append(obj)
        return obj

    def add_media_link(self, note, url, media_type, *, type='media', on_duplicate='error'):
        return self._add_associated_link(collection='media', note=note, url=url,
                                         media_type=media_type, on_duplicate=on_duplicate)

    def add_document(self, note, url, *, media_type='', on_duplicate='error'):
        return self._add_associated_link(collection='documents', note=note, url=url,
                                         media_type=media_type, on_duplicate=on_duplicate)
