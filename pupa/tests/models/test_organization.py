import pytest
from pupa.models import Organization
from validictory import ValidationError


def test_basic_invalid_organization():
    """ Make sure we can make an invalid orga """
    orga = Organization("name")
    orga.add_source(url='foo')
    orga.validate()

    orga.name = None

    with pytest.raises(ValidationError):
        orga.validate()


def test_add_post():
    """ Test that we can hack posts in on the fly'"""
    orga = Organization("name")
    orga.add_source(url='foo')
    orga.validate()

    orga.add_post("Human Readable Name", "Chef")

    assert orga._related[0].role == "Chef"
    assert orga._related[0].label == "Human Readable Name"

    with pytest.raises(TypeError):
        orga.add_identifier("id10t", foo="bar")

    orga.add_identifier("id10t")
    orga.add_identifier("l0l", scheme="kruft")

    assert orga.identifiers[-1]['scheme'] == "kruft"
    assert orga.identifiers[0]['identifier'] == "id10t"
    assert not hasattr(orga.identifiers[0], "scheme")


def test_add_contact():
    """ test we can add a contact detail to an org """
    orga = Organization("name")
    orga.add_source(url='foo')
    orga.validate()

    orga.add_contact_detail(type='voice', value='555-393-2821', note='nothing')

    orga.validate()
