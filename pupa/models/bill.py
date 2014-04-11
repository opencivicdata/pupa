from six import string_types
from .base import BaseModel, AssociatedLinkMixin
from .schemas.bill import schema


def _cleanup_list(obj, default):
    if not obj:
        obj = default
    elif isinstance(obj, string_types):
        obj = [obj]
    elif not isinstance(obj, list):
        obj = list(obj)
    return obj


class Bill(BaseModel, AssociatedLinkMixin):
    """
    An Open Civic Data bill.
    """

    _type = 'bill'
    _schema = schema
    _collection = 'bills'
    __slots__ = ('actions', 'other_names', 'other_titles', 'related_bills', 'name', 'chamber',
                 'documents', 'session', 'sources', 'sponsors', 'summaries', 'subject', 'title',
                 '_openstates_id', 'type', 'versions', 'jurisdiction_id', 'organization',
                 'organization_id', 'identifiers')

    def __init__(self, name, session, title, organization=None, type=None, **kwargs):
        super(Bill, self).__init__()

        self.name = name
        self.session = session
        self.title = title
        self.chamber = None
        self.type = _cleanup_list(type, ['bill'])
        self.organization = organization

        self.actions = []
        self.other_names = []
        self.other_titles = []
        self.documents = []
        self.related_bills = []
        self.sponsors = []
        self.subject = []
        self.summaries = []
        self.versions = []

        for k, v in kwargs.items():
            setattr(self, k, v)

    def add_action(self, description, actor, date, type=None, related_entities=None):
        self.actions.append({
            "description": description,
            "actor": actor,
            "date": date,
            "type": _cleanup_list(type, []),
            "related_entities": related_entities or []  # validate
        })

    def add_related_bill(self, name, session, chamber, relation):
        self.related_bills.append({
            "name": name,
            "session": session,
            "chamber": chamber,
            "relation_type": relation  # validate
        })

    def add_sponsor(self, name, sponsorship_type, entity_type, primary,
                    chamber=None, entity_id=None):
        ret = {
            "name": name,
            "sponsorship_type": sponsorship_type,
            "_type": entity_type,
            "primary": primary,
            "id": entity_id,
            "chamber": chamber,
        }
        self.sponsors.append(ret)

    def add_subject(self, subject):
        self.subject.append(subject)

    def add_summary(self, note, text):
        self.summaries.append({"note": note, "text": text})

    def add_document_link(self, name, url, date=None, type=None, mimetype=None,
                          on_duplicate='error', document_id=None):
        return self._add_associated_link(collection='documents', name=name, url=url, date=date,
                                         type=type, mimetype=mimetype, on_duplicate=on_duplicate,
                                         document_id=document_id)

    def add_version_link(self, name, url, date=None, type=None, mimetype=None,
                         on_duplicate='error', document_id=None):
        return self._add_associated_link(collection='versions', name=name, url=url, date=date,
                                         type=type, mimetype=mimetype, on_duplicate=on_duplicate,
                                         document_id=document_id)

    def __str__(self):
        return self.name + ' in ' + self.session
    __unicode__ = __str__
