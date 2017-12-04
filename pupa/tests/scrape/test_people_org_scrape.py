import datetime
import pytest
from pupa.scrape import Person, Organization, Membership, Post
from pupa.utils import get_pseudo_id
from pupa.exceptions import ScrapeValueError


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
    bob.add_source(url='http://example.com')
    bob.validate()

    bob.name = None

    with pytest.raises(ScrapeValueError):
        bob.validate()


def test_basic_person():
    p = Person('Bob B. Bear')
    p.add_source('http://example.com')
    assert p.name in str(p)
    p.validate()


def test_person_add_membership_org():
    p = Person('Bob B. Bear')
    p.add_source('http://example.com')
    o = Organization('test org', classification='unknown')
    p.add_membership(o, role='member', start_date='2007', end_date=datetime.date(2015, 5, 8))
    assert len(p._related) == 1
    p._related[0].validate()
    assert p._related[0].person_id == p._id
    assert p._related[0].organization_id == o._id
    assert p._related[0].start_date == '2007'
    assert p._related[0].end_date == datetime.date(2015, 5, 8)


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
    with pytest.raises(ScrapeValueError):
        orga.validate()


def test_org_add_post():
    """ Test that we can hack posts in on the fly'"""
    orga = Organization("name", classification="committee")
    orga.add_source(url='http://example.com')
    orga.validate()

    orga.add_post("Human Readable Name", "Chef")

    assert orga._related[0].role == "Chef"
    assert orga._related[0].label == "Human Readable Name"


def test_legislator_related_district():
    leg = Person('John Adams', district='1', primary_org='legislature')
    leg.pre_save('jurisdiction-id')

    assert len(leg._related) == 1
    assert leg._related[0].person_id == leg._id
    assert get_pseudo_id(leg._related[0].organization_id) == {'classification': 'legislature'}
    assert get_pseudo_id(leg._related[0].post_id) ==\
        {"organization__classification": "legislature",
         "label": "1"}


def test_legislator_related_chamber_district():
    leg = Person('John Adams', district='1', primary_org='upper')
    leg.pre_save('jurisdiction-id')

    assert len(leg._related) == 1
    assert leg._related[0].person_id == leg._id
    assert get_pseudo_id(leg._related[0].organization_id) == {'classification': 'upper'}
    assert get_pseudo_id(leg._related[0].post_id) == {"organization__classification": "upper",
                                                      "label": "1"}


def test_legislator_related_chamber_district_role():
    leg = Person('John Adams', district='1', primary_org='lower', role='Speaker')
    leg.pre_save('jurisdiction-id')

    assert len(leg._related) == 1
    assert leg._related[0].person_id == leg._id
    assert get_pseudo_id(leg._related[0].organization_id) == {'classification': 'lower'}
    assert get_pseudo_id(leg._related[0].post_id) == {"organization__classification": "lower",
                                                      "label": "1", "role": "Speaker"}
    assert leg._related[0].role == 'Speaker'


def test_legislator_related_party():
    leg = Person('John Adams', party='Democratic-Republican')
    leg.pre_save('jurisdiction-id')

    # a party membership
    assert len(leg._related) == 1
    assert leg._related[0].person_id == leg._id
    assert get_pseudo_id(leg._related[0].organization_id) == {'classification': 'party',
                                                              'name': 'Democratic-Republican'}
    assert leg._related[0].role == 'member'


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
    assert get_pseudo_id(c._related[0].person_id) == {'name': 'John Adams'}
    assert c._related[0].organization_id == c._id
    assert c._related[0].role == 'member'


def test_person_add_membership_name():
    p = Person('Leonardo DiCaprio')
    p.add_membership('Academy of Motion Picture Arts and Sciences',
                     role='winner', start_date='2016')
    p._related[0].validate()
    assert get_pseudo_id(p._related[0].organization_id) == {
        'name': 'Academy of Motion Picture Arts and Sciences'}
    assert p._related[0].person_id == p._id
    assert p._related[0].role == 'winner'
    assert p._related[0].start_date == '2016'


def test_person_add_party():
    p = Person('Groot')
    p.add_party('Green')
    p._related[0].validate()
    assert get_pseudo_id(p._related[0].organization_id) == {
        'name': 'Green', 'classification': 'party'}


def test_person_add_term():
    p = Person('Eternal')
    p.add_term('eternal', 'council', start_date='0001', end_date='9999')
    p._related[0].validate()
    assert get_pseudo_id(p._related[0].organization_id) == {
        'classification': 'council',
    }
    assert p._related[0].start_date == '0001'
    assert p._related[0].end_date == '9999'
