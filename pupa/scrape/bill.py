from six import string_types
from .base import BaseModel, SourceMixin, AssociatedLinkMixin
from .schemas.bill import schema


def _cleanup_list(obj, default):
    if not obj:
        obj = default
    elif isinstance(obj, string_types):
        obj = [obj]
    elif not isinstance(obj, list):
        obj = list(obj)
    return obj


class Bill(SourceMixin, AssociatedLinkMixin, BaseModel):
    """
    An Open Civic Data bill.
    """

    _type = 'bill'
    _schema = schema

    def __init__(self, name, session, title, from_organization=None, classification=None):
        super(Bill, self).__init__()

        self.name = name
        self.session = session
        self.title = title
        self.chamber = None
        self.classification = _cleanup_list(classification, ['bill'])
        self.from_organization = from_organization

        self.actions = []
        self.other_names = []
        self.other_titles = []
        self.documents = []
        self.related_bills = []
        self.sponsors = []
        self.subject = []
        self.summaries = []
        self.versions = []

    def add_action(self, description, actor, date, type=None, related_entities=None):
        self.actions.append({
            "description": description,
            "actor": actor,
            "date": date,
            "type": _cleanup_list(type, []),
            "related_entities": related_entities or []  # validate
        })

    def add_related_bill(self, name, session, relation_type):
        self.related_bills.append({
            "name": name,
            "session": session,
            "relation_type": relation_type  # enum
        })

    def add_sponsor(self, name, classification, entity_type, primary,
                    chamber=None, entity_id=None):
        ret = {
            "name": name,
            "classification": classification,
            "entity_type": entity_type,
            "primary": primary,
        }
        if entity_type:
            ret[entity_type + '_id'] = entity_id
        self.sponsors.append(ret)

    def add_subject(self, subject):
        self.subject.append(subject)

    def add_summary(self, text, note):
        self.summaries.append({"note": note, "text": text})

    def add_title(self, text, note=''):
        self.other_titles.append({"note": note, "text": text})

    def add_name(self, name, note=''):
        self.other_names.append({"note": note, "name": name})

    def add_document_link(self, name, url, date='', type='', mimetype='', on_duplicate='error'):
        return self._add_associated_link(collection='documents', name=name, url=url, date=date,
                                         type=type, mimetype=mimetype, on_duplicate=on_duplicate)

    def add_version_link(self, name, url, date='', type='', mimetype='', on_duplicate='error'):
        return self._add_associated_link(collection='versions', name=name, url=url, date=date,
                                         type=type, mimetype=mimetype, on_duplicate=on_duplicate)

    def __str__(self):
        return self.name + ' in ' + self.session
    __unicode__ = __str__
