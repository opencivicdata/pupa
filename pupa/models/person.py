from .base import BaseModel
from .membership import Membership
from .schemas.person import schema


class Person(BaseModel):
    """
    Details for a Person in Popolo format.
    """

    _type = 'person'
    _schema = schema
    _collection = 'people'

    __slots__ = ('name', 'gender', 'birth_date',
                 'death_date', 'image', 'summary', 'biography', 'links',
                 'other_names', 'contact_details', '_openstates_id',
                 'chamber', 'district', 'identifiers',
                 'post_id', 'national_identity',)
    _other_name_slots = ('name', 'start_date', 'end_date', 'note')

    def __init__(self, name, **kwargs):
        super(Person, self).__init__()
        self.name = name
        self.biography = None
        self.summary = None
        self.birth_date = None
        self.death_date = None
        self.image = None
        self.gender = None
        self.national_identity = None
        self.links = []
        self.identifiers = []
        self.other_names = []
        self._related = []
        self.contact_details = []

        for k, v in kwargs.items():
            setattr(self, k, v)

    def add_name(self, name, **kwargs):
        other_name = {'name': name}
        for k, v in kwargs.items():
            if k not in self._other_name_slots:
                raise AttributeError('{0} not a valid kwarg for add_name'
                                     .format(k))
            other_name[k] = v
        self.other_names.append(other_name)

    def add_link(self, url, note=None):
        self.links.append({"note": note, "url": url})

    def add_identifier(self, identifier, scheme=None):
        data = {"identifier": identifier}
        if scheme:
            data['scheme'] = scheme
        self.identifiers.append(data)

    def add_contact_detail(self, type, value, note):
        self.contact_details.append({"type": type,
                                     "value": value,
                                     "note": note})

    def add_membership(self, organization, role='member', **kwargs):
        """
            add a membership in an organization and return the membership
            object in case there are more details to add
        """
        membership = Membership(self._id, organization._id, role=role,
                                **kwargs)
        self._related.append(membership)
        return membership

    def __str__(self):
        return self.name
    __unicode__ = __str__

    def __repr__(self):
        as_dict = self.as_dict()
        list(map(as_dict.pop, ('_type', '_id', 'name')))
        args = (self.__class__.__name__, self.name, as_dict)
        return '%s(name=%r, **%r)' % args
