from .base import BaseModel, SourceMixin, ContactDetailMixin, LinkMixin
from .schemas.organization import schema
from .post import Post


class Organization(BaseModel, SourceMixin, ContactDetailMixin, LinkMixin):
    """
    A single popolo encoded Organization
    """

    _type = 'organization'
    _schema = schema

    def __init__(self, name, **kwargs):
        """
        Constructor for the Organization object.
        """
        super(Organization, self).__init__()
        self.name = name
        self.classification = None
        self.founding_date = None
        self.dissolution_date = None
        self.parent_id = None
        self.image = None
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

    def add_identifier(self, identifier, scheme=None):
        data = {"identifier": identifier}
        if scheme:
            data['scheme'] = scheme
        self.identifiers.append(data)

    def add_post(self, label, role, **kwargs):
        post = Post(label=label, role=role, **kwargs)
        self._related.append(post)
