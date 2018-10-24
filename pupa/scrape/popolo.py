import copy
from .base import (BaseModel, SourceMixin, LinkMixin, ContactDetailMixin, OtherNameMixin,
                   IdentifierMixin)
from .schemas.post import schema as post_schema
from .schemas.person import schema as person_schema
from .schemas.membership import schema as membership_schema
from .schemas.organization import schema as org_schema
from ..utils import _make_pseudo_id
from pupa.exceptions import ScrapeValueError

# a copy of the org schema without sources
org_schema_no_sources = copy.deepcopy(org_schema)
org_schema_no_sources['properties'].pop('sources')


class Post(BaseModel, LinkMixin, ContactDetailMixin):
    """
    A popolo-style Post
    """

    _type = 'post'
    _schema = post_schema

    def __init__(self, *, label, role, organization_id=None, chamber=None,
                 division_id=None, start_date='', end_date='',
                 maximum_memberships=1):
        super(Post, self).__init__()
        self.label = label
        self.role = role
        self.organization_id = pseudo_organization(organization_id, chamber)
        self.division_id = division_id
        self.start_date = start_date
        self.end_date = end_date
        self.maximum_memberships = maximum_memberships

    def __str__(self):
        return self.label


class Membership(BaseModel, ContactDetailMixin, LinkMixin):
    """
    A popolo-style Membership.
    """

    _type = 'membership'
    _schema = membership_schema

    def __init__(self, *, person_id, organization_id, post_id=None, role='', label='',
                 start_date='', end_date='', on_behalf_of_id=None,
                 person_name=''
                 ):
        """
        Constructor for the Membership object.

        We require a person ID and organization ID, as required by the
        popolo spec. Additional arguments may be given, which match those
        defined by popolo.
        """
        super(Membership, self).__init__()
        self.person_id = person_id
        self.person_name = person_name
        self.organization_id = organization_id
        self.post_id = post_id
        self.start_date = start_date
        self.end_date = end_date
        self.role = role
        self.label = label
        self.on_behalf_of_id = on_behalf_of_id

    def __str__(self):
        return self.person_id + ' membership in ' + self.organization_id


class Person(BaseModel, SourceMixin, ContactDetailMixin, LinkMixin, IdentifierMixin,
             OtherNameMixin):
    """
    Details for a Person in Popolo format.
    """

    _type = 'person'
    _schema = person_schema

    def __init__(self, name, *, birth_date='', death_date='', biography='', summary='', image='',
                 gender='', national_identity='',
                 # specialty fields
                 district=None, party=None, primary_org='', role='',
                 start_date='', end_date='', primary_org_name=None):
        super(Person, self).__init__()
        self.name = name
        self.birth_date = birth_date
        self.death_date = death_date
        self.biography = biography
        self.summary = summary
        self.image = image
        self.gender = gender
        self.national_identity = national_identity
        if primary_org:
            self.add_term(role, primary_org, district=district,
                          start_date=start_date, end_date=end_date,
                          org_name=primary_org_name)
        if party:
            self.add_party(party)

    def add_membership(self, name_or_org, role='member', **kwargs):
        """
            add a membership in an organization and return the membership
            object in case there are more details to add
        """
        if isinstance(name_or_org, Organization):
            membership = Membership(person_id=self._id,
                                    person_name=self.name,
                                    organization_id=name_or_org._id,
                                    role=role, **kwargs)
        else:
            membership = Membership(person_id=self._id,
                                    person_name=self.name,
                                    organization_id=_make_pseudo_id(name=name_or_org),
                                    role=role, **kwargs)
        self._related.append(membership)
        return membership

    def add_party(self, party, **kwargs):
        membership = Membership(
            person_id=self._id,
            person_name=self.name,
            organization_id=_make_pseudo_id(classification="party", name=party),
            role='member', **kwargs)
        self._related.append(membership)

    def add_term(self, role, org_classification, *, district=None,
                 start_date='', end_date='', label='', org_name=None,
                 appointment=False):
        if org_name:
            org_id = _make_pseudo_id(classification=org_classification,
                                     name=org_name)
        else:
            org_id = _make_pseudo_id(classification=org_classification)

        if district:
            if role:
                post_id = _make_pseudo_id(label=district,
                                          role=role,
                                          organization__classification=org_classification)
            else:
                post_id = _make_pseudo_id(label=district,
                                          organization__classification=org_classification)
        elif appointment:
            post_id = _make_pseudo_id(role=role,
                                      organization__classification=org_classification)
        else:
            post_id = None
        membership = Membership(person_id=self._id, person_name=self.name,
                                organization_id=org_id, post_id=post_id,
                                role=role, start_date=start_date, end_date=end_date, label=label)
        self._related.append(membership)
        return membership

    def __str__(self):
        return self.name


class Organization(BaseModel, SourceMixin, ContactDetailMixin, LinkMixin, IdentifierMixin,
                   OtherNameMixin):
    """
    A single popolo-style Organization
    """

    _type = 'organization'
    _schema = org_schema

    def __init__(self, name, *, classification='', parent_id=None,
                 founding_date='', dissolution_date='', image='',
                 chamber=None):
        """
        Constructor for the Organization object.
        """
        super(Organization, self).__init__()
        self.name = name
        self.classification = classification
        self.founding_date = founding_date
        self.dissolution_date = dissolution_date
        self.parent_id = pseudo_organization(parent_id, chamber)
        self.image = image

    def __str__(self):
        return self.name

    def validate(self):
        schema = None
        # these are implicitly declared & do not require sources
        if self.classification in ('party', 'legislature', 'upper', 'lower', 'executive'):
            schema = org_schema_no_sources
        return super(Organization, self).validate(schema=schema)

    def add_post(self, label, role, **kwargs):
        post = Post(label=label, role=role, organization_id=self._id, **kwargs)
        self._related.append(post)
        return post

    def add_member(self, name_or_person, role='member', **kwargs):
        if isinstance(name_or_person, Person):
            membership = Membership(person_id=name_or_person._id,
                                    person_name=name_or_person.name,
                                    organization_id=self._id,
                                    role=role, **kwargs)
        else:
            membership = Membership(person_id=_make_pseudo_id(name=name_or_person),
                                    person_name=name_or_person,
                                    organization_id=self._id, role=role, **kwargs)
        self._related.append(membership)
        return membership


def pseudo_organization(organization, classification, default=None):
    """ helper for setting an appropriate ID for organizations """
    if organization and classification:
        raise ScrapeValueError('cannot specify both classification and organization')
    elif classification:
        return _make_pseudo_id(classification=classification)
    elif organization:
        if isinstance(organization, Organization):
            return organization._id
        elif isinstance(organization, str):
            return organization
        else:
            return _make_pseudo_id(**organization)
    elif default is not None:
        return _make_pseudo_id(classification=default)
    else:
        return None
