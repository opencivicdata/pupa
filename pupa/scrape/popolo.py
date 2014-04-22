from .base import BaseModel, SourceMixin, LinkMixin, ContactDetailMixin
from .schemas.post import schema as post_schema
from .schemas.person import schema as person_schema
from .schemas.membership import schema as membership_schema
from .schemas.organization import schema as org_schema


class Post(BaseModel, LinkMixin, ContactDetailMixin):
    """
    A popolo-style Post
    """

    _type = 'post'
    _schema = post_schema

    def __init__(self, label, role, organization_id, **kwargs):
        super(Post, self).__init__()
        self.label = label
        self.role = role
        self.organization_id = organization_id
        self.start_date = ''
        self.end_date = ''
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return self.label


class Membership(BaseModel, ContactDetailMixin, LinkMixin):
    """
    A popolo-style Membership.
    """

    _type = 'membership'
    _schema = membership_schema

    def __init__(self, person_id, organization_id, **kwargs):
        """
        Constructor for the Membership object.

        We require a person ID and organization ID, as required by the
        popolo spec. Additional arguments may be given, which match those
        defined by popolo.
        """
        super(Membership, self).__init__()
        self.person_id = person_id
        self.organization_id = organization_id
        self.start_date = ''
        self.end_date = ''
        self.role = ''
        self.label = ''
        self.post_id = None
        self.on_behalf_of_id = None
        self._unmatched_legislator = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        if self.person_id:
            return self.person_id + ' membership in ' + self.organization_id
        else:
            return (self._unmatched_legislator['name'] + ' membership in ' + self.organization_id)
    __unicode__ = __str__


class Person(BaseModel, SourceMixin, ContactDetailMixin, LinkMixin):
    """
    Details for a Person in Popolo format.
    """

    _type = 'person'
    _schema = person_schema

    def __init__(self, name, **kwargs):
        super(Person, self).__init__()
        self.name = name
        self.birth_date = ''
        self.death_date = ''
        self.biography = ''
        self.summary = ''
        self.image = ''
        self.gender = ''
        self.national_identity = ''
        self.identifiers = []
        self.other_names = []
        self._related = []

        for k, v in kwargs.items():
            setattr(self, k, v)

    def add_name(self, name, start_date=None, end_date=None, note=None):
        other_name = {'name': name}
        if start_date:
            other_name['start_date'] = start_date
        if end_date:
            other_name['end_date'] = end_date
        if note:
            other_name['note'] = note
        self.other_names.append(other_name)

    def add_identifier(self, identifier, scheme=None):
        data = {"identifier": identifier}
        if scheme:
            data['scheme'] = scheme
        self.identifiers.append(data)

    def add_membership(self, organization, role='member', **kwargs):
        """
            add a membership in an organization and return the membership
            object in case there are more details to add
        """
        membership = Membership(self._id, organization._id, role=role, **kwargs)
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


class Organization(BaseModel, SourceMixin, ContactDetailMixin, LinkMixin):
    """
    A single popolo encoded Organization
    """

    _type = 'organization'
    _schema = org_schema

    def __init__(self, name, **kwargs):
        """
        Constructor for the Organization object.
        """
        super(Organization, self).__init__()
        self.name = name
        self.classification = None
        self.founding_date = ''
        self.dissolution_date = ''
        self.parent_id = None
        self.image = ''
        self.other_names = []
        self.identifiers = []
        self._related = []
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return self.name
    __unicode__ = __str__

    def __repr__(self):
        as_dict = self.as_dict()
        list(map(as_dict.pop, ('_id', 'name')))
        args = (self.__class__.__name__, self.name, as_dict)
        return '%s(name=%r, **%r)' % args

    def validate(self):
        schema = None
        if self.classification in ['party']:
            # Parties are funny objects. They don't need sources, since
            # they're really not something we scrape directly (well, ever).
            # As a result, we're not going to enforce placing sources on a
            # party object.
            schema = self._schema.copy()
            schema['properties'] = schema['properties'].copy()
            schema['properties'].pop('sources')
        return super(Organization, self).validate(schema=schema)

    @property
    def parent(self):
        return self.parent_id

    @parent.setter
    def parent(self, val):
        self.parent_id = val._id

    def add_identifier(self, identifier, scheme=None):
        data = {"identifier": identifier}
        if scheme:
            data['scheme'] = scheme
        self.identifiers.append(data)

    def add_post(self, label, role, **kwargs):
        post = Post(label=label, role=role, organization_id=self._id, **kwargs)
        self._related.append(post)
