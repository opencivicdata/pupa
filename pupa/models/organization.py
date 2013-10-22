from .base import BaseModel
from .schemas.organization import schema


class Organization(BaseModel):
    """
    A single popolo encoded Organization
    """

    __slots__ = ('classification', 'dissolution_date', 'founding_date',
                 'identifiers', 'name', 'other_names', 'parent_id', 'chamber',
                 'posts', '_openstates_id', 'contact_details', 'division_id',
                 'abbreviation', 'jurisdiction_id', 'identifiers', 'links',)

    _post_slots = ('end_date', 'id', 'label', 'organization_id', 'role',
                   'start_date', 'chamber', 'division_id',
                   'num_seats')

    _type = 'organization'
    _schema = schema
    _collection = 'organizations'

    def __init__(self, name, **kwargs):
        """
        Constructor for the Organization object.
        """
        super(Organization, self).__init__()
        self.links = []
        self.name = name
        self.classification = None
        self.founding_date = None
        self.dissolution_date = None
        self.parent_id = None
        self.other_names = []
        self.identifiers = []
        self.posts = []
        self.contact_details = []
        self._related = []
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return self.name
    __unicode__ = __str__

    def __repr__(self):
        as_dict = self.as_dict()
        list(map(as_dict.pop, ('_type', '_id', 'name')))
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

    def add_link(self, url, note):
        self.links.append({"note": note, "url": url})

    def add_identifier(self, identifier, scheme=None):
        data = {"identifier": identifier}
        if scheme:
            data['scheme'] = scheme
        self.identifiers.append(data)

    def add_post(self, label, role, **kwargs):
        post = {"label": label, "role": role}
        for k, v in kwargs.items():
            if k not in self._post_slots:
                raise AttributeError(
                    '{0} not a valid kwarg for add_post'.format(k))
            post[k] = v
        self.posts.append(post)

    def add_contact_detail(self, type, value, note):
        self.contact_details.append({"type": type,
                                     "value": value,
                                     "note": note})
