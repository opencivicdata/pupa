import copy
from .base import (BaseModel, SourceMixin, LinkMixin, ContactDetailMixin, OtherNameMixin,
                   IdentifierMixin)
from .schemas.post import schema as post_schema
from .schemas.person import schema as person_schema
from .schemas.membership import schema as membership_schema
from .schemas.organization import schema as org_schema

# a copy of the org schema without sources
org_schema_no_sources = copy.deepcopy(org_schema)
org_schema_no_sources['properties'].pop('sources')


class Post(BaseModel, LinkMixin, ContactDetailMixin):
    """
    A popolo-style Post
    """

    _type = 'post'
    _schema = post_schema

    def __init__(self, label, role, organization_id, start_date='', end_date=''):
        super(Post, self).__init__()
        self.label = label
        self.role = role
        self.organization_id = organization_id
        self.start_date = start_date
        self.end_date = end_date

    def __str__(self):
        return self.label
    __unicode__ = __str__


class Membership(BaseModel, ContactDetailMixin, LinkMixin):
    """
    A popolo-style Membership.
    """

    _type = 'membership'
    _schema = membership_schema

    def __init__(self, person_id, organization_id, post_id=None,
                 role='', label='', start_date='', end_date='', on_behalf_of_id=None):
        """
        Constructor for the Membership object.

        We require a person ID and organization ID, as required by the
        popolo spec. Additional arguments may be given, which match those
        defined by popolo.
        """
        super(Membership, self).__init__()
        self.person_id = person_id
        self.organization_id = organization_id
        self.post_id = post_id
        self.start_date = start_date
        self.end_date = end_date
        self.role = role
        self.label = label
        self.on_behalf_of_id = on_behalf_of_id

    def __str__(self):
        return self.person_id + ' membership in ' + self.organization_id
    __unicode__ = __str__


class Person(BaseModel, SourceMixin, ContactDetailMixin, LinkMixin, IdentifierMixin,
             OtherNameMixin):
    """
    Details for a Person in Popolo format.
    """

    _type = 'person'
    _schema = person_schema

    def __init__(self, name, birth_date='', death_date='', biography='', summary='', image='',
                 gender='', national_identity=''):
        super(Person, self).__init__()
        self.name = name
        self.birth_date = birth_date
        self.death_date = death_date
        self.biography = biography
        self.summary = summary
        self.image = image
        self.gender = gender
        self.national_identity = national_identity

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


class Organization(BaseModel, SourceMixin, ContactDetailMixin, LinkMixin, IdentifierMixin,
                   OtherNameMixin):
    """
    A single popolo-style Organization
    """

    _type = 'organization'
    _schema = org_schema

    def __init__(self, name, classification=None, parent_id=None, chamber='',
                 founding_date='', dissolution_date='', image=''):
        """
        Constructor for the Organization object.
        """
        super(Organization, self).__init__()
        self.name = name
        self.classification = classification
        self.chamber = chamber
        self.founding_date = founding_date
        self.dissolution_date = dissolution_date
        self.parent_id = parent_id
        self.image = image

    def __str__(self):
        return self.name
    __unicode__ = __str__

    def validate(self):
        schema = None
        if self.classification in ['party']:
            schema = org_schema_no_sources
        return super(Organization, self).validate(schema=schema)

    #@property
    #def parent(self):
    #    return self.parent_id

    #@parent.setter
    #def parent(self, val):
    #    self.parent_id = val._id

    def add_post(self, label, role, **kwargs):
        post = Post(label=label, role=role, organization_id=self._id, **kwargs)
        self._related.append(post)
        return post
