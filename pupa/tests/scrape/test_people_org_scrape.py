import pytest
from pupa.scrape import Person, Organization, Membership, Post
from pupa.utils import get_psuedo_id
from validictory import ValidationError


def test_basic_post():
    post = Post(label='1', role='Representative', organization_id='fake_org')
    assert '1' in str(post)
    post.validate()


def test_basic_invalid_post():
    post = Post(label=1, role='Representative', organization_id='fake_org')
    with pytest.raises(ValueError):
        post.validate()


def test_basic_membership():
    m = Membership(person_id='person', organization_id='org')
    assert 'person' in str(m) and 'org' in str(m)


def test_basic_invalid_membership():
    membership = Membership(person_id=33, organization_id="orga_id")
    with pytest.raises(ValueError):
        membership.validate()


def test_basic_invalid_person():
    bob = Person("Bob B. Johnson")
    bob.add_source(url='foo')
    bob.validate()

    bob.name = None

    with pytest.raises(ValidationError):
        bob.validate()


def test_basic_person():
    p = Person('Bob B. Bear')
    p.add_source('http://example.com')
    assert p.name in str(p)
    p.validate()


def test_person_add_membership():
    p = Person('Bob B. Bear')
    p.add_source('http://example.com')
    o = Organization('test org', classification='unknown')
    p.add_membership(o, role='member', start_date='2007')
    assert len(p._related) == 1
    p._related[0].validate()
    assert p._related[0].person_id == p._id
    assert p._related[0].organization_id == o._id
    assert p._related[0].start_date == '2007'


def test_basic_organization():
    org = Organization('some org', classification='committee')
    org.add_source('http://example.com')
    assert org.name in str(org)
    org.validate()


def test_no_source_on_party_org():
    org = Organization('Hat', classification='party')
    # no source? no problem because classification = party
    org.validate()


def test_basic_invalid_organization():
    orga = Organization("name")

    # no source
    with pytest.raises(ValidationError):
        orga.validate()


def test_org_add_post():
    """ Test that we can hack posts in on the fly'"""
    orga = Organization("name", classification="committee")
    orga.add_source(url='foo')
    orga.validate()

    orga.add_post("Human Readable Name", "Chef")

    assert orga._related[0].role == "Chef"
    assert orga._related[0].label == "Human Readable Name"


def test_legislator_related_district():
    l = Person('John Adams', district='1', primary_org='legislature')
    l.pre_save('jurisdiction-id')

    assert len(l._related) == 1
    assert l._related[0].person_id == l._id
    assert get_psuedo_id(l._related[0].organization_id) == {'classification': 'legislature'}
    assert get_psuedo_id(l._related[0].post_id) == {"organization__classification": "legislature",
                                                    "label": "1"}
    assert l._related[0].role == 'member'


def test_legislator_related_chamber_district():
    l = Person('John Adams', district='1', primary_org='upper')
    l.pre_save('jurisdiction-id')

    assert len(l._related) == 1
    assert l._related[0].person_id == l._id
    assert get_psuedo_id(l._related[0].organization_id) == {'classification': 'upper'}
    assert get_psuedo_id(l._related[0].post_id) == {"organization__classification": "upper",
                                                    "label": "1"}
    assert l._related[0].role == 'member'


def test_legislator_related_party():
    l = Person('John Adams', party='Democratic-Republican')
    l.pre_save('jurisdiction-id')

    # a party membership
    assert len(l._related) == 1
    assert l._related[0].person_id == l._id
    assert get_psuedo_id(l._related[0].organization_id) == {'classification': 'party',
                                                            'name': 'Democratic-Republican'}
    assert l._related[0].role == 'member'


def test_committee_add_member_person():
    c = Organization('Defense', classification='committee')
    p = Person('John Adams')
    c.add_member(p, role='chairman')
    assert c._related[0].person_id == p._id
    assert c._related[0].organization_id == c._id
    assert c._related[0].role == 'chairman'


def test_committee_add_member_name():
    c = Organization('Defense', classification='committee')
    c.add_member('John Adams')
    assert get_psuedo_id(c._related[0].person_id) == {'name': 'John Adams'}
    assert c._related[0].organization_id == c._id
    assert c._related[0].role == 'member'
