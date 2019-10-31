from ..utils import _make_pseudo_id
from .base import BaseModel, SourceMixin, AssociatedLinkMixin, LinkMixin
from .schemas.event import schema
from pupa.exceptions import ScrapeValueError


class EventAgendaItem(dict, AssociatedLinkMixin):
    event = None

    def __init__(self, description, event):
        super(EventAgendaItem, self).__init__({
            "description": description,
            "classification": [],
            "related_entities": [],
            "subjects": [],
            "media": [],
            "notes": [],
            "order": str(len(event.agenda)),
            "extras": {},
        })
        self.event = event

    def add_subject(self, what):
        self['subjects'].append(what)

    def add_classification(self, what):
        self['classification'].append(what)

    def add_vote_event(self, vote_event, *, id=None, note='consideration'):
        self.add_entity(name=vote_event, entity_type='vote_event', id=id, note=note)

    def add_committee(self, committee, *, id=None, note='participant'):
        self.add_entity(name=committee, entity_type='organization', id=id, note=note)

    def add_bill(self, bill, *, id=None, note='consideration'):
        self.add_entity(name=bill, entity_type='bill', id=id, note=note)

    def add_person(self, person, *, id=None, note='participant'):
        self.add_entity(name=person, entity_type='person', id=id, note=note)

    def add_media_link(self, note, url, media_type, *, text='', type='media',
                       on_duplicate='error'):
        return self._add_associated_link(collection='media', note=note, url=url, text=text,
                                         media_type=media_type, on_duplicate=on_duplicate)

    def add_entity(self, name, entity_type, *, id, note):
        ret = {
            "name": name,
            "entity_type": entity_type,
            "note": note
        }
        if id:
            ret['id'] = id
        elif entity_type:
            if entity_type in ('organization', 'person'):
                id = _make_pseudo_id(name=name)
            elif entity_type in ('bill', 'vote_event'):
                id = _make_pseudo_id(identifier=name)
            else:
                raise ScrapeValueError('attempt to call add_entity with unsupported '
                                       'entity type: {}'.format(entity_type))
            ret[entity_type + '_id'] = id

        self['related_entities'].append(ret)


class Event(BaseModel, SourceMixin, AssociatedLinkMixin, LinkMixin):
    """
    Details for an event in .format
    """
    _type = 'event'
    _schema = schema

    def __init__(self, name, start_date, location_name, *,
                 all_day=False, description="", end_date="",
                 status="confirmed", classification="event"
                 ):
        super(Event, self).__init__()
        self.start_date = start_date
        self.all_day = all_day
        self.end_date = end_date
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
        return '{} {}'.format(self.start_date, self.name.strip())

    def set_location(self, name, *, note="", url="", coordinates=None):
        self.location = {"name": name, "note": note, "url": url, "coordinates": coordinates}

    def add_participant(self, name, type, *, id=None, note='participant'):
        p = {
            "name": name,
            "entity_type": type,
            "note": note
        }
        if id:
            p['id'] = id
        elif type:
            id = _make_pseudo_id(name=name)
            p[type + '_id'] = id

        self.participants.append(p)

    def add_person(self, name, *, id=None, note='participant'):
        return self.add_participant(name=name, type='person', id=id, note=note)

    def add_committee(self, name, *, id=None, note='participant'):
        return self.add_participant(name=name, type='organization', id=id, note=note)

    def add_agenda_item(self, description):
        obj = EventAgendaItem(description, self)
        self.agenda.append(obj)
        return obj

    def add_media_link(self, note, url, media_type, *, text='',
                       type='media', on_duplicate='error', date=''):
        return self._add_associated_link(collection='media',
                                         note=note,
                                         url=url,
                                         text=text,
                                         media_type=media_type,
                                         on_duplicate=on_duplicate,
                                         date=date)

    def add_document(self, note, url, *, text='', media_type='', on_duplicate='error', date=''):
        return self._add_associated_link(collection='documents',
                                         note=note, url=url,
                                         text=text,
                                         media_type=media_type,
                                         on_duplicate=on_duplicate,
                                         date=date)
