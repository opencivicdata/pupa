from django.db import models
from .base import CommonBase, ContactDetailBase, LinkBase, IdentifierBase, OtherNameBase
from .jurisdiction import Jurisdiction


class Organization(CommonBase):
    name = models.CharField(max_length=300)
    image = models.URLField(blank=True)
    parent = models.ForeignKey('self', related_name='children')
    jurisdiction = models.ForeignKey(Jurisdiction, related_name='organizations')
    classification = models.CharField(max_length=100, blank=True)   # enum
    chamber = models.CharField(max_length=10, blank=True)
    # TODO: division_id link
    founding_date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]
    dissolution_date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]


class OrganizationIdentifier(IdentifierBase):
    organization = models.ForeignKey(Organization, related_name='identifiers')


class OrganizationName(OtherNameBase):
    organization = models.ForeignKey(Organization, related_name='other_names')


class OrganizationContactDetail(ContactDetailBase):
    organization = models.ForeignKey(Organization, related_name='contact_details')


class OrganizationLink(LinkBase):
    organization = models.ForeignKey(Organization, related_name='links')


class OrganizationSource(LinkBase):
    organization = models.ForeignKey(Organization, related_name='sources')


class Post(CommonBase):
    label = models.CharField(max_length=300, blank=True)
    role = models.CharField(max_length=300, blank=True)
    organization = models.ForeignKey(Organization, related_name='posts')
    start_date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]
    end_date = models.CharField(max_length=10)    # YYYY[-MM[-DD]]


class PostContactDetail(ContactDetailBase):
    post = models.ForeignKey(Post, related_name='contact_details')


class PostLinks(LinkBase):
    post = models.ForeignKey(Post, related_name='contact_details')


class Person(CommonBase):
    name = models.CharField(max_length=300)
    image = models.URLField(blank=True)
    gender = models.CharField(max_length=100)
    summary = models.CharField(max_length=500)
    national_identity = models.CharField(max_length=300)
    biography = models.TextField()
    birth_date = models.CharField(max_length=10, blank=True)    # YYYY[-MM[-DD]]
    death_date = models.CharField(max_length=10, blank=True)    # YYYY[-MM[-DD]]


class PersonIdentifier(IdentifierBase):
    person = models.ForeignKey(Person, related_name='identifiers')


class PersonName(OtherNameBase):
    person = models.ForeignKey(Person, related_name='other_names')


class PersonContactDetail(ContactDetailBase):
    person = models.ForeignKey(Person, related_name='contact_details')


class PersonLink(LinkBase):
    person = models.ForeignKey(Person, related_name='links')


class PersonSource(LinkBase):
    person = models.ForeignKey(Person, related_name='sources')


class Membership(CommonBase):
    organization = models.ForeignKey(Organization, related_name='memberships')
    person = models.ForeignKey(Person, related_name='memberships')
    post = models.ForeignKey(Post, related_name='posts', null=True)
    on_behalf_of = models.ForeignKey(Organization, related_name='memberships_on_behalf_of')
    label = models.CharField(max_length=300, blank=True)
    role = models.CharField(max_length=300, blank=True)
    start_date = models.CharField(max_length=10, blank=True)    # YYYY[-MM[-DD]]
    end_date = models.CharField(max_length=10, blank=True)      # YYYY[-MM[-DD]]


class MembershipContactDetail(ContactDetailBase):
    membership = models.ForeignKey(Membership, related_name='contact_details')


class MembershipLink(LinkBase):
    membership = models.ForeignKey(Membership, related_name='links')
