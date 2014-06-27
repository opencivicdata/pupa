import pytest
from pupa.scrape import Person, Organization, Membership, Post
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
    o = Organization('test org')
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
